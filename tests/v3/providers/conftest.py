import importlib
import pkgutil

import pytest

import azbankgateways.v3.factories as factories
from azbankgateways.v3.interfaces import ProviderConfigInterface, ProviderInterface
from azbankgateways.v3.providers import __path__ as providers_path


@pytest.fixture(scope="session")
def discover_provider_modules() -> None:
    """
    Dynamically import all provider modules to ensure all subclasses of ProviderInterface are loaded.
    """
    for module_info in pkgutil.walk_packages(providers_path, prefix="azbankgateways.v3.providers."):
        importlib.import_module(module_info.name)


@pytest.fixture(scope="session")
def provider_classes(discover_provider_modules: None) -> list[type[ProviderInterface]]:
    return ProviderInterface.__subclasses__()


@pytest.fixture(scope="session")
def provider_config_factory_pairs(
    provider_classes: list[type[ProviderInterface]],
) -> list[tuple[type[ProviderInterface], type[ProviderConfigInterface]]]:
    provider_config_factory_pairs = []

    for provider_class in provider_classes:
        provider_class_name = provider_class.__name__
        provider_name_prefix = provider_class_name.replace('Provider', '')
        provider_config_factory = getattr(factories, f'{provider_name_prefix}ProviderConfigFactory', None)

        if not provider_config_factory:
            raise AssertionError(
                f"No ProviderConfigFactory found for provider: {provider_class.__name__} in factories"
            )

        provider_config_factory_pairs.append((provider_class, provider_config_factory))

    return provider_config_factory_pairs
