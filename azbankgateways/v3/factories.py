from factory.base import Factory
from factory.declarations import Sequence

from azbankgateways.v3.http import URL
from azbankgateways.v3.providers.zarinpal import ZarinpalProviderConfig


class ZarinpalProviderConfigFactory(Factory[ZarinpalProviderConfig]):
    class Meta:
        model = ZarinpalProviderConfig

    merchant_code = Sequence(lambda n: f"zarinpal-merchant-code-{n}")  # type: ignore[no-untyped-call]
    callback_url_generator = lambda order: URL(  # noqa: E731
        f"https://zarinpal-dummy-callback.dummy/order/{order.order_id}"
    )
