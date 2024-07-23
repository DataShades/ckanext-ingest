[![Tests](https://github.com/DataShades/ckanext-ingest/workflows/Tests/badge.svg)](https://github.com/DataShades/ckanext-ingest/actions/workflows/test.yml)

# ckanext-ingest

Framework for transforming data stream into tasks.

This extension provides tools for reading user-provided file-like object and
producing tasks based on the input. Use it if you need to read records from
CSV/JSON/XLSX/etc. file and:

* create or update datasets using information from these records
* remove users/organizations/datasets based on record details
* send email to user specified by every record
* collect some sort of statistics
* perform any type of work that can be described as a series of steps

## Requirements

Compatibility with core CKAN versions:

| CKAN version | Compatible? |
|--------------|-------------|
| 2.9          | no          |
| 2.10         | yes         |
| 2.11         | yes         |
| master       | yes         |


## Installation

To install ckanext-ingest:

1. Install it via **pip**:
   ```sh
   pip install ckanext-ingest

   ## with basic XLSX strategy
   # pip install 'ckanext-ingest[xlsx]'
   ```
1. Add `ingest` to the `ckan.plugins` setting in your CKAN config file.

## Usage

Data can be ingested into CKAN via `ingest_import_records` API action. It
requires a `source` with the data, and it's recommended to pass an extraction
`strategy`, to get a full control over the process.

```sh
ckanapi action ingest_import_records source@path/to/data.zip strategy="myext:extract_archive"
```

But before anything can be ingested you have to regiser a `strategy` that
produces `records`. `strategy` defines how source is parsed and divided into
data chunks, and `record` wraps single data chunk and perform actions using
information from the chunk.

`strategy` is registered via `IIngest` interface. It has to be a subclass of
`ckanext.ingest.shared.ExtractionStrategy`. The only requirement for
`strategy` is to return iterable of `records` from its `extract` method.

`record` is created by `strategy` and it has to be a subclass of
`ckanext.ingest.shared.Record`. Its `ingest` method is responsible for
ingestion: depending on the record purpose, it can create/update/delete data or
perform any other task that has sense.


## Examples

### Register custom strategy

```python

import ckan.plugins as p

from ckanext.ingest.interfaces import IIngest

class MyPlugin(p.SingletonPlugin):
    p.implements(IIngest)

    def get_ingest_strategies(self):
        return {
          "my:custom_strategy": CustomStrategy,
        }

```

### Strategy thay reads JSON file and creates a single dataset from it.
```python
import ckan.plugins.toolkit as tk
from ckanext.ingest.shared import ExtractionStrategy, Storage, Record, IngestionResult

class SingleJsonStrategy(ExtractionStrategy):

    def extract(self, source: Storage, options):
        # source is a readable IO stream(werkzeug.datastructures.FileStorage)
        data = json.load(source)

        # `extract` returns iterable over records. When the strategy produces
        # a single record, this record can be either yielded or returned as
        # a list with a single element
        yield SimplePackageRecord(data, {})

class SimplePackageRecord(Record):
    def ingest(self, context: ckan.types.Context) -> IngestionResult:

        dataset = tk.get_action("package_create")(context, self.data)

        # `ingest` returns a brief overview of the ingestion result
        return {
            "success": True,
            "result": dataset,
            "details": {}
        }

```

### Strategy that reads from CSV names of organizations that must be removed from the portal

```python
import csv
import ckan.plugins.toolkit as tk
from ckanext.ingest.shared import ExtractionStrategy, Record

class DropOrganizationsUsingCsvStrategy(ExtractionStrategy):

    def extract(self, source, options):
        # `source` is an `IO[bytes]`, so we turn in into `IO[str]`
        str_stream = StringIO(source.read().decode())
        rows = csv.DictReader(st_stream)

        for row in rows:
            # record's constructor requires two arguments:
            # the raw data and the mapping with record options.
            yield DropOrganiationRecord(row, {})

class DropOrganizationRecord(Record):
    def ingest(self, context: ckan.types.Context):
        try:
            tk.get_action("organization_delete")(context, {"id": self.data["name"]})
        except tk.ObjectNotFound:
            success = False
        else:
            success = True

        return {
            "success": success,
            "result": None,
            "details": {}
        }

```

### Pull datasets from CKAN instance specified in JSON(like ckanext-harvest), and remove datasets that were not updated during ingestion

```python
import json
from datetime import datetime
from ckanapi import RemoteCKAN
import ckan.plugins.toolkit as tk
from ckanext.ingest.shared import ExtractionStrategy, Record

class HarvestStrategy(ExtractionStrategy):

    def extract(self, source, options):
        details = json.load(source)
        client = RemoteCKAN(**details)

        now = datetime.utcnow()

        # produce a record that creates a package for every remote dataset
        for dataset in client.action.package_search()["results"]:
            yield SimpleDatasetRecord(row, {})

        # produce an additional record that removes stale datasets
        # (datasets that were modified before ingestion started and were
        # not updated during current ingestion)
        yield DeleteStaleDatasetsRecord({"before": now}, {})

class SimplePackageRecord(Record):
    def ingest(self, context: ckan.types.Context) -> IngestionResult:

        dataset = tk.get_action("package_create")(context, self.data)

        return {
            "success": True,
            "result": dataset,
            "details": {"remote_id": self.data["id"]}
        }


class DeleteStaleDatasetsRecord(Record):
    def ingest(self, context: ckan.types.Context) -> IngestionResult:
        before = self.data["before"].isoformat()
        result = tk.get_action("package_search")(
            context,
            {"fq": f"metadata_modified:[* TO {before}]", "fl": "id"}
        )

        deleted = []
        for dataset in result["results"]
            tk.get_action("package_delete")(context, {"id": dataset["id"]})
            deleted.append(id)

        return {
            "success": True,
            "result": deleted,
            "details": {"count": len(deleted), "before": before}
        }

```

## Advanced

To get the most from ingestion workflows, try writing reusable strategies and
records using details below

### Strategy autodetection

`strategy` argument for actions is optional. When it missing, the plugins
chooses the most appropriate strategy for the ingested source. This feature
relies on `can_handle` and `must_handle` methods of the extraction
strategy. Both methods receive the mimetype of the source and the source itself
and return `True`/`False`.

Among all strategies that return `True` from `can_handle`, plugin selects the
first strategy that returns `True` from `must_handle` as well. If there is no
such strategy, the first `can_handle` wins.

`ckanext.ingest.shared.ExtractionStrategy` defines both these
methods. `must_handle` always returns `False`. `can_handle` return `True` if
source's mimetype is listed in `mimetypes` property of the handler:

```python
class ExtractionStrategy:
    mimetypes: ClassVar[set[str]] = set()

    @classmethod
    def can_handle(cls, mime: str | None, source) -> bool:
        return mime in cls.mimetypes

    @classmethod
    def must_handle(cls, mime, source) -> bool:
        return False

```

If you want to register strategy that can handle JSON sources, just register
strategy with an appropriate `mimetypes`:

```python
class JsonStrategy(ExtractionStrategy):
    mimetypes = {"application/json"}
```

If there are more than one strategy that supports JSON mimetype, the first
registered strategy is selected. If you want to register strategy that always
handles JSON sources with specific name(`DRINK_ME.json`), disregarding the
order, you can use `must_handle`.

Note, that `must_handle` is checked only when `can_handle` returns `True`, so
we still using default `mimetypes` logic:

```python
class DrinkMeJsonStrategy(ExtractionStrategy):
    mimetypes = {"application/json"}

    @classmethod
    def must_handle(cls, mime, source: Storage) -> bool:
        return source.filename == "DRINK_ME.json"
```

### Record factories

`ExtractionStrategy` has a default implementation of `extract`. This default
implementation calls `chunks` method to parse the source and get ingestable
data fragments. Then, for every data chunk `chunk_into_record` method is
called, to transform arbitrary data into a `Record`. Finally, `extract` yields
whatever is produced by `chunk_into_record`.

Default implementation of `chunks` ignores the source and returns an empty
list. As result, by default any source produce zero records and nothing happens.

The first thing you can do to produce a data is overriding `chunks`.

If you are working with CSV file, `chunks` can return rows from the file:

```python
class CsvRowsStrategy(ExtractionStrategy):
    mimetypes = {"text/csv"}

    def chunks(self, source, options) -> Iterable[Any]:
        str_stream = StringIO(source.read().decode())
        rows = csv.reader(str_stream)

        yield from rows
```

Such strategy will produce `ckanext.ingest.shared.Record` for every row of the
source CSV. But base `Record` class doesn't do much, so you need to replace it
with your own `Record` subclass.

As mentioned before, data chunk converted into a record via `chunk_into_record`
method. You can either override it, or use default implemmentation, which
creates instances of the class stored under `record_factory` attribute of the
strategy. Default value of this attribute is `ckanext.ingest.shared.Record` and
if you want to use a different record implementation, do the following:

```python
class CsvRowsStrategy(ExtractionStrategy):
    record_factory = MyCustomRecord
    ...
```

### Strategy delegation

`ExtractionStrategy.extract` method is responsible for producing records. But
it doesn't mean that strategy have to generate records itself. Instead,
strategy can do some preparations and use another strategy in order to make records.

Let's imagine `UrlStrategy` that accepts file with a single line - URL of the
remote portal - and pulls data from this portal. As we don't know the
type of the data, we cannot tell, how records can be created from it. So, when
data is fetched, we can use its mimetype to select the most suitable strategy
and delegate record generation to its `extract` method:

```python
import requests
import magic
from io import BytesIO
from ckanext.ingest import shared

class UrlStrategy(ExtractionStrategy):

    def extract(self, source, options) -> Iterable[Any]:
        # read URL from file-like source
        url = source.read()
        resp = requests.get(url)

        # convert response bytes into `source`
        sub_source = shared.make_storage(BytesIO(resp.content))

        # identify mimetype
        mime = magic.from_buffer(sub_source.read(1024))
        sub_source.seek(0)

        # choose the appropriate strategy
        handler = shared.get_handler_for_mimetype(mime, sub_source)

        # delegate extraction
        if handler:
            yield from handler.extract(source, options)
```

### Strategy and Record options

`ExtractionStrategy.extract` and `Record.ingest` accept second argument
`options`. In both cases it's a dictionary that can be used to modify the logic
inside corresponding methods. Strategy options described by
`ckanext.ingest.shared.StrategyOptions`, and record options described by
`ckanext.ingest.shared.RecordOptions`.

Keys defined on the top-level, have sense for every strategy/record. For
example, `RecordOptions` defines `update_existing` flag. If record that creates
data detects existing conflicting entity, `update_existing` flag should be
taken into account when the record is considering what to do in such case. It's
only a recomendation and this flag can be ignored or you can use a different
option. But using common options simplify understanding of the workflow.

For strategy there are 3 common keys:

* `record_options`: these options should be passed into every record produced
  by the strategy(`RecordOptions`)
* `nested_strategy`: if strategy delegates record creation to a different
  strategy, `nested_strategy` should be prefered over auto-detected
  strategy(mimetype detection)
* `locator`: if source is represented by some kind of collection, `locator` is
  a callable that returns specific members of collection. It can be used when
  parsing archives, so that strategy can extract package's metadata from one
  file and upload resources returned by `locator` into it. Or, when parsing
  XLSX, `locator` can return sheets by title to simplify processing of multiple
  sheets.

For any options that can be used only by a specific strategy, there is an
`extras` option inside both `StrategyOptions` and `RecordOptions`. This
dictionary can hold any data and there are no expectations to its structure.

Keys that are used often inside `extras` may eventually be added as recommended
options to the top-level. But, as these are only recomendations, you can just
ignore them and pass whatever data you need as options.

### Data transformation in Record

`ckanext.ingest.shared.Record` class requires two parameters for
initialization: `raw` data and `options` for the record. When record is
created, it calls its `trasform` method, that copies `raw` data into `data`
property. This is the best place for data mapping, before record's `ingest`
method is called. If you want to remove all empty members from record's `data`,
it can be done in the following way:

```python
class DenseRecord(Record):
    def transform(self, raw: Any):
        self.data = {
            key: value
            for key, value in raw.items()
            if value is not None
        }

```

### Record ingestion and results

Record usually calls one of CKAN API actions during ingestion. In order to do
it properly, record needs action `context`, which is passed as as single
argument into `ingest` method. But this is only the most common workflow, so if
you don't use any action, just ignore the `context`. What is more important, is
the output of the `ingest`. It must be a dictionary described by
`ckanext.ingest.shared.IngestionResult`. It has three members:

* `success`: flag that indicates whether ingestion succeeded or failed
* `result`: data produced by ingestion(package, resource, organization, etc.)
* `details`: any other details that may be useful. For example, how many
  entities were modified during ingestion, which API action was used, what were
  the errors if ingestion failed.

These details are not required by ingestion, but they may be used for building
ingestion report.

### Configure record trasformation with ckanext-scheming

`ckanext.ingest.record` module contains `PackageRecord` and `ResourceRecord`
classes that create package/resource. But their `trasform` method is much more
interesting. It maps `raw` into `data` using field configuration from metadata
schema defined by ckanext-scheming.

In order to configure mapping, add `ingest_options` attribute to the field defition:
```yaml
- field_name: title
  label: Title
  ingest_options: {}
```

During transformation, every key in `raw` is checked agains the schema. If
schema contains field with `ingest_options` whose `field_name` or `label`
matches the key from `raw`, this key is copied into `data` and mapped to the
corresponding `field_name`. I.e, for the field definition above, both `raw`
versions - `{"title": "hello"}` and `{"Title": "hello"}` will turn into `data`
with value `{"title": "hello"}`.

If you have completely different names in `raw`, use `aliases`(`list[str]`)
attribute of `ingest_options`:

```yaml
- field_name: title
  label: Title
  ingest_options:
      aliasses: [TITLE, "name of the dataset"]
```

In this case, `{"name of the dataset": "hello"}` and `{"TITLE": "hello"}` will
turn into `{"title": "hello"}`.

If value requires additional processing before it can be used as a field
values, specify all applied validators as `convert` attribute of the
`ingest_options`:

```yaml
- field_name: title
  label: Title
  ingest_options:
      convert: conver_to_lowercase json_list_or_string
```

`convert` uses the same syntax as `validators` attribute of the field
definition. You can use any registered validator inside this field. But, unlike
validators, if `Invalid` error raised during transformation, field is silently
ignored and ingestion continues.

Any field from `raw` that has no corresponding field in schema(detected by
`field_name`/`label` or `ingest_options.aiases`), is not added to the `data`
and won't be used for package/resource creation.

### Generic strategies

There are a number of strategies available out-of-the box. You probably won't
use them as-is, but creating a subclass of these strategies may simplify the
process and solve a couple of common problems.

#### `ingest:scheming_csv`

Defined by `ckanext.ingest.strategy.csv.CsvStrategy`.

#### `ingest:recursive_zip`

Defined by `ckanext.ingest.strategy.zip.CsvStrategy`.

#### `ingest:xlsx`

Defined by `ckanext.ingest.strategy.xlsx.XlsxStrategy`.

## Configuration

```ini
# List of allowed ingestion strategies. If empty, all registered strategies
# are allowed
# (optional, default: )
ckanext.ingest.strategy.allowed = ingest:recursive_zip

# List of disabled ingestion strategies.
# (optional, default: )
ckanext.ingest.strategy.disabled = ingest:scheming_csv

# Base template for WebUI
# (optional, default: page.html)
ckanext.ingest.base_template = admin/index.html

# Allow moving existing resources between packages.
# (optional, default: false)
ckanext.ingest.allow_resource_transfer = true

# Rename strategies using `{"import.path.of:StrategyClass": "new_name"}` JSON
# object
# (optional, default: )
ckanext.ingest.strategy.name_mapping = {"ckanext.ingest.strategy.zip:ZipStrategy": "zip"}
```

## Interfaces

`ckanext.ingest.interfaces.IIngest` interface implementations can regiser
custom extraction strategies via `get_ingest_strategies` method::

```python
def get_ingest_strategies() -> dict[str, type[ckanext.ingest.shared.ExtractionStrategy]]:
    """Return extraction strategies."""
    return {
        "my_plugin:xlsx_datasets": MyXlsxStrategy,
    }
```

## API

### `ingest_extract_records`

Extract records from the source.

This method mainly exists for debugging. It doesn't create anything, just
parses the source, produces records and return record's data as a
list. Because it aggregates all extracted records into a single list, it
can consume a lot of memory. If you want to iterate over, consider using
`iter_records` function that produces an iterable over records.

Args:

    source: str|FileStorage - data source for records

    strategy: str|None - record extraction strategy. If missing, strategy
    is guessed depending on source's mimetype

    options: SourceOptions - dictionary with configuration for strategy and
    records. Consumed by strategies so heavily depends on the chosen
    strategy.


### `ingest_import_records`

Ingest records extracted from source.

Parse the source, convert it into Records using selected strategy, and call
`Record.ingest`, potentially creating/updating data.

Args:

    source: str|FileStorage - data source for records

    strategy: str|None - record extraction strategy. If missing, strategy
    is guessed depending on source's mimetype

    options: SourceOptions - dictionary with configuration for strategy and
    records. Consumed by strategies so heavily depends on the chosen
    strategy.

    defaults: dict[str, Any] - default data added to every record(if missing)

    overrides: dict[str, Any] - data that unconditionally overrides record details

    skip: int - number of records that are skipped without ingestion

    take: int - max number of records that will be ingested
