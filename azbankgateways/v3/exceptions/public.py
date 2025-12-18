from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import TYPE_CHECKING, Any


class AZBankException(Exception):
    default_message = "An error occurred in AZBank gateway."

    def __init__(self, message: str | None = None, *args: Any) -> None:
        super().__init__(*args)
        self.message = message or self.default_message
