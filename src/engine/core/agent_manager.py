from __future__ import annotations

import asyncio
import functools
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from piedpiper_engine.engine import Engine
    from piedpiper_engine.engine import ClientToQueues


class AgentManager:
    """Agent Manager class that manages running agents and returning the output
    of any agent that has finished."""

    def __init__(self, engine: Engine = None) -> None:
        """Create an instance of AgentManager with an optional Engine
        Args:
            engine: pied_piper Engine instance

        Raises:
            NoEngineError: Engine is not given at the initialization step
        """

        self.__engine = engine
        self.__loop = engine.get_loop()
        self.__tasks = []

    def __clear_finished_tasks(self) -> None:
        """Filters out finished tasks from the tasks list"""

        self.__tasks = list(
            filter(
                lambda task: (task.done() is False),
                self.__tasks,
            )
        )

    async def to_process(self, ctq: ClientToQueues) -> None:
        """to_process method that will extract the client messages and use a
        ThreadPool to execute the agents with the messages, and outputs
        the result from the agent to the engine.
        Args:
            ctq: ClientToQueues instance of the client
        """

        with ThreadPoolExecutor() as pool:
            while ctq.client_queue.is_empty() is False:
                self.__tasks.append(
                    self.__loop.run_in_executor(
                        pool,
                        functools.partial(
                            ctq.agents[0].process,
                            ctq.client._id,
                            ctq.client_queue.get_next_message(),
                        ),
                    )
                )

            for result in asyncio.as_completed(self.__tasks):
                self.__clear_finished_tasks()

                agent_out = await result

                self.__engine.add_agent_output(agent_out[0], agent_out[1])

    def quit(self) -> None:
        # self.agent_processor.cancel_all()
        pass
