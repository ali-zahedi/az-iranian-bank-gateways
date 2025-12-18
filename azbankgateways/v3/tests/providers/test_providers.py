import importlib
import inspect
import pkgutil
from typing import Any, Set, Type

import pytest

from azbankgateways.v3.interfaces import ProviderInterface
from azbankgateways.v3.providers import __path__ as providers_path


@pytest.fixture(autouse=True)
def discover_provider_modules() -> None:
    """
    Dynamically import all provider modules to ensure all subclasses
    of ProviderInterface are loaded.
    """
    for module_info in pkgutil.walk_packages(providers_path, prefix="azbankgateways.v3.providers."):
        importlib.import_module(module_info.name)


def get_init_params(cls: Type[Any]) -> Set[str]:
    """Return the set of parameter names for a class __init__, excluding 'self'."""
    sig = inspect.signature(cls.__init__)
    return {p for p in sig.parameters if p != "self"}


def test_provider_init_signature_and_attributes() -> None:
    """
    Verify that each ProviderInterface subclass:
    1. Defines its own __init__ method.
    2. Matches required parameters from the interface.
    3. Sets instance attributes for each parameter.
    """
    subclasses = ProviderInterface.__subclasses__()
    assert subclasses, "No ProviderInterface subclasses found."

    interface_params = get_init_params(ProviderInterface)

    for provider_class in subclasses:
        # 1. Ensure subclass defines its own __init__
        assert (
            "__init__" in provider_class.__dict__
        ), f"{provider_class.__name__} must define its own __init__() method"

        # 2. Validate signature matches interface
        subclass_params = get_init_params(provider_class)
        assert subclass_params == interface_params, (
            f"{provider_class.__name__}.__init__ parameter mismatch.\n"
            f"Expected: {interface_params}\n"
            f"Found: {subclass_params}"
        )
