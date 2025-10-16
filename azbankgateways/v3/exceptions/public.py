from typing import Optional


class AZBankPublicExceptions(Exception):
    default_message = "An error occurred in AZBank gateway."

    def __init__(self, message: Optional[str] = None, *args):
        super().__init__(*args)
        self.message = message or self.default_message
