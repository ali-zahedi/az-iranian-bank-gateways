from __future__ import annotations

from dataclasses import fields, is_dataclass
from types import UnionType
from typing import TYPE_CHECKING, get_args, get_origin


if TYPE_CHECKING:
    from azbankgateways.v3.exceptions.internal import AZBankInternalException


class CheckDataclassFieldsMixin:
    def check_fields(self, error_class: type[AZBankInternalException]) -> None:
        if not is_dataclass(self):
            raise TypeError(
                f"{self.__class__.__name__} must be a dataclass to use CheckDataclassFieldsMixin."
            )

        for config_field in fields(self):
            annotation = config_field.type
            field_name = config_field.name
            value = getattr(self, field_name)

            origin = get_origin(annotation)
            args = get_args(annotation)

            # --- Handle Union types ---
            if isinstance(annotation, UnionType):
                if not any(isinstance(value, arg) for arg in args):
                    raise error_class(
                        f"Field '{field_name}' must be one of {args}, got {type(value).__name__}"
                    )
                continue

            # --- Handle non-generic simple types ---
            if origin is None:
                if not value:
                    raise error_class(f"Field '{field_name}' cannot be empty/null")
                if not isinstance(value, annotation):
                    raise error_class(
                        f"Field '{field_name}' must be of type {annotation}, got {type(value).__name__}"
                    )
                continue
