from __future__ import annotations

from typing import IO, Optional, Type
from .base import Handler, ParsingStrategy
from .. import registry

__all__ = ["Handler", "get_handler", "ParsingStrategy"]

strategies = registry.Registry[Type[ParsingStrategy]]()


def get_handler(mime: Optional[str], source: IO[bytes]) -> Optional[Handler]:
    choices = []
    for strategy in strategies:
        if not strategy.can_handle(mime, source):
            continue

        if strategy.must_handle(mime, source):
            return Handler(strategy())

        choices.append(strategy)

    if choices:
        return Handler(choices[0]())
