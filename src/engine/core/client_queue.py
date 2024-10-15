
from .client import Client


class ClientQueue:
    def __init__(self, client: Client):
        self._messages: list[str] = []
        self._client = client
        self._is_new = True

    def is_client(self, client: Client) -> bool:
        if client._id == self._client._id:
            return True
        return False

    def is_client_by_id(self, client_id):
        if client_id == self._client._id:
            return True
        return False

    def get_client_id(self):
        return self._client._id

    def add_message(self, input: str):
        self._messages.append(input)
        self._is_new = True

    def get_next_message(self):
        if len(self._messages) > 0:
            message = self._messages[0]
            self._messages.pop(0)
            self._is_new = False
            return message
        self._is_new = False
        return None

    def is_empty(self):
        return len(self._messages) == 0

    def get_length(self):
        return len(self._messages)
