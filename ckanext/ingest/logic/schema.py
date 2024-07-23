from __future__ import annotations

import cgi
import mimetypes
from io import BytesIO
from typing import Any

import magic

import ckan.plugins.toolkit as tk
from ckan import types
from ckan.logic.schema import validator_args

from ckanext.ingest import artifact, shared


def into_report(value: Any):
    """Transform value into report object."""
    if isinstance(value, artifact.Artifacts):
        return value

    try:
        return artifact.make_artifacts(value)
    except KeyError as err:
        msg = f"Unsupported report type: {value} ({type(value)})"
        raise tk.Invalid(msg) from err


def into_uploaded_file(value: Any):
    """Try converting value into shared.Storage object."""
    if isinstance(value, shared.Storage):
        return value

    if isinstance(value, cgi.FieldStorage):
        if not value.filename or not value.file:
            raise ValueError(value)

        mime, _encoding = mimetypes.guess_type(value.filename)
        if not mime:
            mime = magic.from_buffer(value.file.read(1024), True)
            value.file.seek(0)

        return shared.make_storage(value.file, value.filename, mime)

    if isinstance(value, str):
        value = value.encode()

    if isinstance(value, bytes):
        stream = BytesIO(value)
        mime = magic.from_buffer(stream.read(1024), True)
        stream.seek(0)
        return shared.make_storage(stream, mimetype=mime)

    msg = f"Unsupported source type: {type(value)}"
    raise tk.Invalid(msg)


@validator_args
def extract_records(
    not_missing: types.Validator,
    default: types.ValidatorFactory,
    one_of: types.ValidatorFactory,
    convert_to_json_if_string: types.Validator,
    dict_only: types.Validator,
    ignore_missing: types.Validator,
    natural_number_validator: types.Validator,
) -> types.Schema:
    return {
        "source": [not_missing, into_uploaded_file],
        "strategy": [ignore_missing, one_of(shared.strategies.keys())],
        "options": [
            default('{"record_options": {}}'),
            convert_to_json_if_string,
            dict_only,
        ],
        "skip": [default(0), natural_number_validator],
        "take": [ignore_missing, natural_number_validator],
    }


@validator_args
def import_records(
    default: types.ValidatorFactory,
    convert_to_json_if_string: types.Validator,
    dict_only: types.Validator,
    one_of: types.ValidatorFactory,
) -> types.Schema:
    schema = extract_records()
    schema.update(
        {
            "report": [default("stats"), into_report],
            "defaults": [default("{}"), convert_to_json_if_string, dict_only],
            "overrides": [default("{}"), convert_to_json_if_string, dict_only],
        },
    )

    return schema
