from __future__ import annotations

from abc import ABCMeta, abstractmethod
from decimal import Decimal
from typing import TYPE_CHECKING, Type, TypeVar

from azbankgateways.v3.exceptions.internal import InternalMinimumAmountError
from azbankgateways.v3.http import HttpClient, HttpRequest
from azbankgateways.v3.interfaces import ProviderInterface


if TYPE_CHECKING:
    from azbankgateways.v3.interfaces import MessageServiceInterface, OrderDetails

T = TypeVar("T", bound="Provider")


class ProviderMeta(ABCMeta):
    def __call__(
        cls: Type[T],
        config,
        message_service: MessageServiceInterface,
        http_client: HttpClient,
        http_request_cls: type[HttpRequest],
    ) -> T:
        return super().__call__(
            config=config,
            message_service=message_service,
            http_client=http_client,
            http_request_cls=http_request_cls,
        )


class Provider(ProviderInterface, metaclass=ProviderMeta):
    def __init__(
        self,
        config,
        message_service: MessageServiceInterface,
        http_client: HttpClient,
        http_request_cls: type[HttpRequest],
    ) -> None:
        self.config = config
        self.message_service = message_service
        self.http_client = http_client
        self.http_request_cls = http_request_cls

    def check_minimum_amount(self, order_details: OrderDetails) -> None:
        if order_details.amount < self.minimum_amount:
            raise InternalMinimumAmountError(order_details, self.minimum_amount)

    @property
    @abstractmethod
    def minimum_amount(self) -> Decimal:
        raise NotImplementedError("Subclasses must implement the `minimum_amount` property.")

    @abstractmethod
    def create_payment_request(self, order_details: OrderDetails) -> HttpRequest:
        raise NotImplementedError("Subclasses must implement `create_payment_request`.")
