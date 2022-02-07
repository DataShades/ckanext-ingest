from __future__ import annotations

import mimetypes
import logging
from typing import IO, Any, Iterable, Optional
import zipfile
from .base import ParsingStrategy, ParsingExtras


log = logging.getLogger(__name__)

class ZipStrategy(ParsingStrategy):
    def _make_locator(self, archive: zipfile.ZipFile):
        def locator(name: str):
            try:
                return archive.open(name)
            except KeyError:
                log.warning(
                    "File %s not found in the archive %s", name, archive.filename
                )

        return locator

    def extract(
        self, source: IO[bytes], extras: Optional[ParsingExtras] = None
    ) -> Iterable[Any]:
        from . import get_handler
        with zipfile.ZipFile(source) as archive:
            for item in archive.namelist():
                mime, _encoding = mimetypes.guess_type(item)
                handler = get_handler(mime)
                if not handler:
                    log.debug("Skip %s with MIMEType %s", item, mime)
                    continue

                handler.parse(
                    archive.open(item), {"file_locator": self._make_locator(archive)}
                )

                yield from handler.records
