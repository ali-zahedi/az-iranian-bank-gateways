from __future__ import annotations

from typing import TYPE_CHECKING
from typing import cast

from azbankgateways.v3.interfaces import MessageServiceInterface
from azbankgateways.v3.interfaces import MessageType

if TYPE_CHECKING:
    from typing import Any


class MessageService(MessageServiceInterface):
    # TODO: Temp solution
    def __init__(self) -> None:
        self.__default_messages = {
            MessageType.DESCRIPTION: "Purchase with tracking code - {tracking_code}",
            MessageType.TIMEOUT_ERROR: "Timeout while connecting to {url} with data {data}",
            MessageType.CONNECTION_ERROR: "Connection error while connecting to {url} with data {data}",
            MessageType.REJECTED_PAYMENT: "Gateway rejected payment",
            MessageType.MINIMUM_AMOUNT: "Minimum amount is {minimum_amount}",
        }
        self.__message_parameters = {
            MessageType.DESCRIPTION: ["tracking_code"],
            MessageType.TIMEOUT_ERROR: ["url", "data"],
            MessageType.CONNECTION_ERROR: ["url", "data"],
            MessageType.REJECTED_PAYMENT: [],
            MessageType.MINIMUM_AMOUNT: ["minimum_amount"],
        }

    def generate_message(self, key: MessageType, context: dict[str, Any]) -> str:
        message_template = context.get(f"{key.value}_template", self.__default_messages.get(key, ""))
        return cast(str, message_template.format(**context))

    def get_required_parameters(self, key: MessageType) -> list[str] | None:
        return self.__message_parameters.get(key)
