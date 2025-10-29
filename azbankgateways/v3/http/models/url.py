from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class URL:
    value: str

    def __post_init__(self) -> None:
        parsed = urlparse(self.value)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid URL: {self.value}")

        normalized = self.value if self.value.endswith("/") else self.value + "/"
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"URL({self.value!r})"

    def join(self, path: str) -> str:
        """Join a relative path to this base URL"""
        return self.value.rstrip("/") + "/" + path.lstrip("/")
