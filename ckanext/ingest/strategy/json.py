from __future__ import annotations

import json
import logging

from typing import Any, Iterable

from ckanext.ingest import shared


log = logging.getLogger(__name__)


class ListStrategy(shared.ExtractionStrategy):
    """Extract records from JSON."""

    mimetypes = {"application/json"}

    def chunks(
        self,
        source: shared.Storage,
        options: shared.StrategyOptions,
    ) -> Iterable[dict[str, Any]]:
        yield from json.loads(source.read())
