from __future__ import annotations

import importlib
import pkgutil
from typing import TYPE_CHECKING

import azbankgateways.v3.factories as factories
from azbankgateways.v3.interfaces import ProviderInterface
from azbankgateways.v3.providers import __path__ as providers_path


if TYPE_CHECKING:
    from azbankgateways.v3.interfaces import ProviderConfigInterface


def discover_provider_classes() -> list[type[ProviderInterface]]:
    for module_info in pkgutil.walk_packages(providers_path, prefix="azbankgateways.v3.providers."):
        importlib.import_module(module_info.name)

    provider_classes = ProviderInterface.__subclasses__()
    return provider_classes


def get_provider_config_factory_pairs() -> (
    list[tuple[type[ProviderInterface], type[ProviderConfigInterface]]]
):
    pairs = []

    provider_classes = discover_provider_classes()

    for provider_class in provider_classes:
        provider_class_name = provider_class.__name__
        provider_name_prefix = provider_class_name.replace('Provider', '')
        provider_config_factory = getattr(factories, f'{provider_name_prefix}ProviderConfigFactory', None)

        if not provider_config_factory:
            raise AssertionError(
                f"No ProviderConfigFactory found for provider: {provider_class.__name__} in factories"
            )

        pairs.append((provider_class, provider_config_factory))

    return pairs
