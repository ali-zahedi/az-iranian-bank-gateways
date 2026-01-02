from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, ContextManager, Iterator, Protocol

import pytest


if TYPE_CHECKING:
    from syrupy.assertion import SnapshotAssertion

    class ExceptionAssertion(Protocol):
        def __call__(self, *, snapshot_name: str = ...) -> ContextManager[None]:
            pass


@pytest.fixture
def capture_exception(snapshot: SnapshotAssertion) -> ExceptionAssertion:
    """
    Fixture to capture and assert exceptions match a snapshot.

    Usage:
        def test_raises(capture_exception: ExceptionAssertion):
            with capture_exception():
                raise ValueError("something went wrong")
    """

    @contextmanager
    def _assert(
        *,
        snapshot_name: str = "expected_exception",
    ) -> Iterator[None]:
        try:
            yield
        except Exception as exc:
            exc_text = _format_exception(exc)
            assert exc_text == snapshot(name=snapshot_name)

    return _assert


def _format_exception(
    exc: Exception,
) -> str:
    """Format exception for snapshot comparison."""
    exc_info = pytest.ExceptionInfo.from_exception(exc)
    return exc_info.exconly()
