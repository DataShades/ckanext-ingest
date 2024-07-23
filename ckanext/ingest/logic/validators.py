from __future__ import annotations

import uuid
from typing import Any

from ckan.lib import munge

NAMESPACE_INGEST = uuid.uuid5(uuid.NAMESPACE_DNS, "ingest")


def ingest_into_uuid(value: str):
    return str(uuid.uuid5(NAMESPACE_INGEST, value))


def ingest_munge_name(value: str):
    return munge.munge_name(value)


def ingest_strip_prefix(prefix: str):
    def validator(value: Any):
        if isinstance(value, str) and value.startswith(prefix):
            value = value[len(prefix) :]
        return value

    return validator
