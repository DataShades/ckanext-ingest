from __future__ import annotations

import logging
import itertools
from typing import Any


import ckan.plugins.toolkit as tk
from ckan.logic import validate
from ..artifact import make_artifacts

from ckanext.toolbelt.decorators import Collector

from . import schema
from .. import strategy

log = logging.getLogger(__name__)
action, get_actions = Collector("ingest").split()


@action
@validate(schema.extract_records)
def extract_records(context, data_dict) -> list[dict[str, Any]]:
    tk.check_access("ingest_extract_records", context, data_dict)
    records = _extract_records(data_dict)

    return [r.data for r in records]


@action
@validate(schema.import_records)
def import_records(context, data_dict):
    tk.check_access("ingest_import_records", context, data_dict)

    start = data_dict.get("start", 0)
    rows = data_dict.get("rows")
    if rows is not None:
        rows += start

    artifacts = make_artifacts(data_dict["report"])
    records = _extract_records(data_dict)

    for record in itertools.islice(records, start, rows):
        record.set_options(data_dict)
        record.fill(data_dict["defaults"], data_dict["overrides"])
        try:
            result = record.ingest({"user": context["user"]})
        except tk.ValidationError as e:
            artifacts.fail({"error": e.error_dict, "source": record.raw})
        except tk.ObjectNotFound as e:
            artifacts.fail(
                {"error": e.message or "Package does not exists", "source": record.raw}
            )

        else:
            artifacts.success({"result": result})

    return artifacts.collect()


def _extract_records(data_dict: dict[str, Any]):
    mime = data_dict["source"].content_type
    handler = strategy.get_handler(mime, data_dict["source"].stream)

    if not handler:
        raise tk.ValidationError(
            {"source": [tk._("Unsupported MIMEType {mime}").format(mime=mime)]}
        )

    return handler.parse(data_dict["source"].stream)
