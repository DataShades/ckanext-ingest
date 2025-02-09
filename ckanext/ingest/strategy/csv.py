from __future__ import annotations
import contextlib
import chardet
import csv
import logging
from io import StringIO
from typing import Any, Iterable

from ckanext.ingest import shared
from ckanext.ingest.record import PackageRecord

log = logging.getLogger(__name__)


class CsvSimpleStrategy(shared.ExtractionStrategy):
    """Extract records from CSV."""

    mimetypes = {"text/csv", "application/csv"}

    def chunks(
        self,
        source: shared.Storage,
        options: shared.StrategyOptions,
    ) -> Iterable[dict[str, Any]]:
        reader_options: dict[str, Any] = shared.get_extra(options, "reader_options", {})
        encoding = reader_options.get("encoding")
        content = source.read()
        if not encoding:
            encoding = chardet.detect(content)["encoding"]
        if not encoding:
            encoding = "utf8"

        str_stream = StringIO(content.decode(encoding))
        if "dialect" not in reader_options:
            sample = str_stream.read(1024)
            str_stream.seek(0)
            with contextlib.suppress(csv.Error):
                dialect = csv.Sniffer().sniff(sample)
                reader_options = dict(reader_options, dialect=dialect)

        return csv.DictReader(str_stream, **reader_options)


class CsvStrategy(CsvSimpleStrategy):
    """Transform CSV records into datasets using ckanext-scheming.

    Every scheming field that has `ingest_options` attribute defines how data
    from the row maps into metadata schema. For example, if `notes` field has
    `ingest_options: {aliases: [DESCRIPTION]}`, `DESCRIPTION` column from CSV
    will be used as a data source for this field.

    """

    record_factory = PackageRecord
