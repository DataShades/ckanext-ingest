from __future__ import annotations
import dataclasses
from typing import Any, NamedTuple, Optional, Union
from typing_extensions import TypeAlias
import ckan.plugins.toolkit as tk
from ckanext.scheming.validation import validators_from_string

TransformationSchema: TypeAlias = "dict[str, Rules]"


@dataclasses.dataclass
class Options:
    alias: Optional[str] = None
    normalize_choice: bool = False
    choice_separator: str = ", "
    convert: str = ""


class Rules(NamedTuple):
    options: Options
    field: dict[str, Any]
    schema: dict[str, Any]


def transform_package(
    data_dict: dict[str, Any], type_: str = "dataset"
) -> dict[str, Any]:
    schema = _get_transformation_schema(type_, "dataset")
    result = _transform(data_dict, schema)
    result.setdefault("type", type_)
    return result


def transform_resource(
    data_dict: dict[str, Any], type_: str = "dataset"
) -> dict[str, Any]:
    schema = _get_transformation_schema(type_, "resource")
    return _transform(data_dict, schema)


def _get_transformation_schema(type_: str, fieldset: str) -> TransformationSchema:
    schema = tk.h.scheming_get_dataset_schema(type_)
    if not schema:
        raise TypeError(f"Schema {type_} does not exist")
    fields = f"{fieldset}_fields"

    return {
        f["field_name"]: Rules(Options(**(f["ingest_options"] or {})), f, schema)
        for f in schema[fields]
        if "ingest_options" in f
    }


def _transform(data: dict[str, Any], schema: TransformationSchema) -> dict[str, Any]:
    result = {}

    for field, rules in schema.items():
        k = rules.options.alias or rules.field["label"]

        if k not in data:
            continue

        validators = validators_from_string(
            rules.options.convert, rules.field, rules.schema
        )
        valid_data, _err = tk.navl_validate({field: data[k]}, {field: validators})

        value = valid_data[field]
        if value == "":
            continue

        if rules.options.normalize_choice:
            value = _normalize_choice(
                value,
                tk.h.scheming_field_choices(rules.field),
                rules.options.choice_separator,
            )
        result[field] = value

    return result


def _normalize_choice(
    value: Union[str, list[str], None], choices: list[dict[str, str]], separator: str
) -> Union[str, list[str], None]:
    if not value:
        return

    if not isinstance(value, list):
        value = value.split(separator)

    mapping = {o["label"]: o["value"] for o in choices if "label" in o}
    value = [mapping.get(v, v) for v in value]

    if len(value) > 1:
        return value

    return value[0]
