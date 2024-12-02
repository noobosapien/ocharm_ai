import uuid
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from piedpiper_engine.engine import Engine


class Client:
    """Client class: the interface between the user and the engine."""

    def __init__(
        self,
        id: str = None,
        engine=None,
        callback: Callable[[str, str], None] = None,
    ) -> None:
        """Create an instance of Client with an optional id, user_id, engine, and a callback.
        Args:
            id: The id of the instance in the engine
            user_id: Custom user identifier
            engine: pied_piper Engine instance
            callback: Function callback when output is ready

        Raises:
            NoEngineError: Engine is not given at the initialization step
            NoCallbackError: No callback function given at the initialization step
            NoUserIdError: No user_id given at the initialization step
        """
        self._engine = engine
        self._callback = callback

        if id is None:
            self._id = uuid.uuid4().hex
        else:
            self._id = id

    def get_id(self) -> str:
        """Return the custom defined user_id of the client"""
        return self._id

    def add_engine(self, engine) -> None:
        """Adds the pied_piper engine instance to work with"""
        if self._engine is None:
            self._engine = engine

    def add_message(self, input) -> None:
        """Adds a message to the engine with the self's _id"""
        if self._engine is not None:
            self._engine.add_message(self._id, input)

    def output(self, output) -> None:
        """Calls the callback given while output is present"""
        # if self._callback is not None:
        #     self._callback(self._id, output.get().serialize())
        pass
