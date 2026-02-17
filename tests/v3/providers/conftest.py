import importlib
import pkgutil

import pytest

import azbankgateways.v3.factories as factories
from azbankgateways.v3.http import HTTPClient
from azbankgateways.v3.interfaces import (
    HTTPHeadersInterface,
    HTTPRequestInterface,
    ProviderConfigInterface,
    ProviderInterface,
)
from azbankgateways.v3.message_services import MessageService
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
def provider_config_pairs(
    provider_classes: list[type[ProviderInterface]],
    message_service: MessageService,
    http_client: HTTPClient,
    http_request_class: type[HTTPRequestInterface],
    http_headers_class: type[HTTPHeadersInterface],
) -> list[tuple[ProviderInterface, ProviderConfigInterface]]:
    provider_config_factory_pairs = []

    for provider_class in provider_classes:
        provider_class_name = provider_class.__name__
        provider_name_prefix = provider_class_name.replace('Provider', '')
        provider_config_factory = getattr(factories, f'{provider_name_prefix}ProviderConfigFactory', None)

        if not provider_config_factory:
            raise AssertionError(
                f"No ProviderConfigFactory found for provider: {provider_class.__name__} in factories"
            )

        config = provider_config_factory()
        provider = provider_class(
            config=config,
            message_service=message_service,
            http_client=http_client,
            http_request_class=http_request_class,
            http_headers_class=http_headers_class,
        )
        provider_config_factory_pairs.append((provider, config))

    return provider_config_factory_pairs
