from __future__ import annotations


class AZBankException(Exception):
    default_message = "An error occurred in AZBank gateway."

    def __init__(self, message: str | None = None, *args):
        super().__init__(*args)
        self.message = message or self.default_message
