from typing import Any, Dict, Optional

from azbankgateways.v3.interfaces import MessageServiceInterface, MessageType


class MessageService(MessageServiceInterface):
    # TODO: Temp solution
    def __init__(self):
        self.__default_messages = {
            MessageType.DESCRIPTION: "Purchase with tracking code - {tracking_code}",
            MessageType.TIMEOUT_ERROR: "Timeout while connecting to {request.url} with data {request.data}",
            MessageType.CONNECTION_ERROR: (
                "Connection error while connecting to {request.url} " "with data {request.data}"
            ),
            MessageType.REJECTED_PAYMENT: "Gateway rejected payment",
            MessageType.MINIMUM_AMOUNT: "Minimum amount is {minimum_amount}",
        }
        self.__message_parameters = {
            MessageType.DESCRIPTION: ["tracking_code"],
            MessageType.TIMEOUT_ERROR: ["url", "data"],
            MessageType.CONNECTION_ERROR: ["url", "data"],
            MessageType.REJECTED_PAYMENT: [],
            MessageType.MINIMUM_AMOUNT: ['minimum_amount'],
        }

    def generate_message(self, key: MessageType, context: Dict[str, Any]) -> str:
        message_template = context.get(f"{key.value}_template", self.__default_messages.get(key, ""))
        return message_template.format(**context)

    def get_required_parameters(self, key: MessageType) -> Optional[list]:
        return self.__message_parameters.get(key)
