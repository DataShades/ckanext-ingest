from __future__ import annotations

import itertools
import logging
import mimetypes
from typing import Any, Iterable

import ckan.plugins.toolkit as tk
from ckan import types
from ckan.logic import validate

from ckanext.ingest import shared

from . import schema

log = logging.getLogger(__name__)


@tk.side_effect_free
@validate(schema.extract_records)
def ingest_extract_records(
    context: types.Context,
    data_dict: dict[str, Any],
) -> list[dict[str, Any]]:
    """Extract records from the source.

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

    """
    tk.check_access("ingest_extract_records", context, data_dict)
    records = iter_records(data_dict)

    start = data_dict["skip"]
    stop = data_dict.get("take")
    if stop is not None:
        stop += start

    return [r.data for r in itertools.islice(records, start, stop)]


@validate(schema.import_records)
def ingest_import_records(context: types.Context, data_dict: dict[str, Any]):
    """Ingest records extracted from source.

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
    """
    tk.check_access("ingest_import_records", context, data_dict)

    start = data_dict["skip"]
    stop = data_dict.get("take")
    if stop is not None:
        stop += start

    report = data_dict["report"]
    records = iter_records(data_dict)

    for record in itertools.islice(records, start, stop):
        record.fill(data_dict["defaults"], data_dict["overrides"])

        try:
            result = record.ingest(tk.fresh_context(context))
            log.debug("Record ingestion: %s", result)

        except tk.ValidationError as e:
            log.debug("Validation error: %s. Record: %s", e.error_dict, record)
            report.fail({"error": e.error_dict, "source": record.raw})

        except tk.ObjectNotFound as e:
            log.debug("Object not found: %s. Record: %s", e, record)
            report.fail(
                {
                    "error": e.message or "Not found",
                    "source": record.raw,
                },
            )

        except Exception as e:
            log.exception("Unexpected ingestion error for record %s", record)
            report.fail(
                {
                    "error": str(e),
                    "source": record.raw,
                },
            )

        else:
            report.success({"result": result})

    return report.collect()


def iter_records(data_dict: dict[str, Any]) -> Iterable[shared.Record]:
    """Produce iterable over all extracted records.

    When `strategy` is present in `data_dict`, it explicitly defines extraction
    strategy. If `strategy` is missing, the most suitable strategy is chosen
    depending on `source`'s mimetype.

    """
    source: shared.Storage = data_dict["source"]

    if "strategy" in data_dict:
        parser = shared.strategies[data_dict["strategy"]]()

    else:
        mime = None

        if source.filename:
            mime, _encoding = mimetypes.guess_type(source.filename)

        if not mime:
            mime = data_dict["source"].content_type

        parser = shared.get_handler_for_mimetype(mime, data_dict["source"])

        if not parser:
            raise tk.ValidationError(
                {"source": [tk._("Unsupported MIMEType {mime}").format(mime=mime)]},
            )

    return parser.extract(data_dict["source"], data_dict["options"])
