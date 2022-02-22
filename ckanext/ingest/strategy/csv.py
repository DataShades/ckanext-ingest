from __future__ import annotations
from io import StringIO

import logging
from typing import IO, Iterable, Optional, Type
import csv

from .base import ParsingStrategy, ParsingExtras
from ..record import Record, PackageRecord


log = logging.getLogger(__name__)


class CsvStrategy(ParsingStrategy):
    mimetypes = {"text/csv"}

    def extract(
        self, source: IO[bytes], extras: Optional[ParsingExtras] = None
    ) -> Iterable[Record]:

        reader = csv.DictReader(StringIO(source.read().decode()))
        yield from map(self._record_factory(source), reader)

    def _record_factory(self, source: IO[bytes]) -> Type[Record]:
        return PackageRecord