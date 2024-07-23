from __future__ import annotations

import dataclasses
from typing import Any

from typing_extensions import TypeAlias

import ckan.plugins.toolkit as tk

TransformationSchema: TypeAlias = "dict[str, Field]"

_default = object()


@dataclasses.dataclass
class Options:
    """Transformation options.

    This information is taken from `{profile}_options` attribute of field in
    ckanext-scheming's schema.

    These options define how raw value passed into the Record transforms into
    proper value that is suitable for the entity's schema. Workflow is the
    following:

    * parse the source
    * get raw data dict
    * transform every field defined in metadata schema and available in raw
      data using Options into
    * pass transformed data to CKAN API action

    """

    # names of the field in the raw data
    aliases: list[str] = dataclasses.field(default_factory=list)

    # transform select label[s] into value[s]
    normalize_choice: bool = False

    # used by `normalize_choice`. Split raw value into multiple values using
    # given separator
    choice_separator: str = ", "

    # convert raw field using validators. Validation errors are ignored.
    convert: str = ""

    # use default value when field is missing
    default: Any = _default

    def __post_init__(self):
        if isinstance(self.aliases, str):
            self.aliases = [self.aliases]


@dataclasses.dataclass
class Field:
    """Metadata field details."""

    # transformation options
    options: Options
    # field definition
    field: dict[str, Any]
    # whole metadata schema
    schema: dict[str, Any]


def transform_package(
    data_dict: dict[str, Any],
    type_: str = "dataset",
    profile: str = "ingest",
) -> dict[str, Any]:
    """Transform raw data into package_create/package_update payload.

    Every schema field that has `{profile}_options` attribute will be
    transformed from raw data using these options. Fields in schema that do not
    have `{profile}_options` attribute are ignored.

    """
    schema = _get_transformation_schema(type_, "dataset_fields", profile)
    result = _transform(data_dict, schema)
    result.setdefault("type", type_)
    return result


def transform_resource(
    data_dict: dict[str, Any],
    type_: str = "dataset",
    profile: str = "ingest",
) -> dict[str, Any]:
    """Transform raw data into resource_create/resource_update payload.

    Every schema field that has `{profile}_options` attribute will be
    transformed from raw data using these options. Fields in schema that do not
    have `{profile}_options` attribute are ignored.

    """
    schema = _get_transformation_schema(type_, "resource_fields", profile)
    return _transform(data_dict, schema)


def _get_transformation_schema(
    type_: str,
    fieldset: str,
    profile: str,
) -> TransformationSchema:
    """Parse metadata schema into transformation schema."""
    schema = tk.h.scheming_get_dataset_schema(type_)
    if not schema:
        raise ValueError(type_)

    return {
        f["field_name"]: Field(Options(**(f[f"{profile}_options"] or {})), f, schema)
        for f in schema[fieldset]
        if f"{profile}_options" in f
    }


def _transform(data: dict[str, Any], schema: TransformationSchema) -> dict[str, Any]:
    """Transform raw data using transformation schema."""
    from ckanext.scheming.validation import validators_from_string

    validators_from_string: Any

    result: dict[str, Any] = {}

    for field, rules in schema.items():
        for k in rules.options.aliases or [
            rules.field["label"],
            rules.field["field_name"],
        ]:
            if k in data:
                break
        else:
            if rules.options.default is _default:
                continue
            k = field
            data[k] = rules.options.default

        validators = validators_from_string(
            rules.options.convert,
            rules.field,
            rules.schema,
        )
        valid_data, _err = tk.navl_validate(data, {k: validators})

        # field was removed by one of ignore_* validators
        if k not in valid_data:
            continue

        value = valid_data[k]
        if rules.options.normalize_choice:
            value = _normalize_choice(
                value,
                tk.h.scheming_field_choices(rules.field),
                rules.options.choice_separator,
            )
        result[field] = value

    return result


def _normalize_choice(
    value: Any,
    choices: list[dict[str, str]],
    separator: str,
) -> str | list[str] | None:
    """Transform select label[s] into corresponding value[s]."""
    if not value:
        return None

    if isinstance(value, str):
        value = value.split(separator)

    mapping = {o["label"]: o["value"] for o in choices if "label" in o}
    value = [mapping.get(v, v) for v in value]

    if len(value) > 1:
        return value

    return value[0]
