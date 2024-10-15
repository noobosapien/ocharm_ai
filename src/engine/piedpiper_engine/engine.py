import asyncio

from dotenv import load_dotenv

from engine.core.agent import Agent
from engine.core.agent_manager import AgentManager
from engine.core.agent_queue import AgentQueue
from engine.core.client import Client
from engine.core.client_manager import ClientManager
from engine.core.client_queue import ClientQueue

from .engine_manager_thread import EngineManagerThread

load_dotenv()


class ClientToQueues:
    """ClientToQueues class that maps agents to the client and holds their queues"""

    def __init__(
        self, client: Client, client_queue: ClientQueue, agent_queue: AgentQueue
    ) -> None:
        """Create an instance of ClientToQueues class, agents must be manually
        added and they are initialized as an empty list.
        Args:
            client: The client instance of Client
            client_queue: The queue for the client instance of ClientQueue
            agent_queue: The queue for the agent instances of AgentQueue
        """

        self.client = client
        self.client_queue = client_queue
        self.agents = []
        self.agent_queue = agent_queue


class Engine:
    def __init__(self) -> None:
        self._all_queues: list[ClientToQueues] = []
        self._loop = asyncio.new_event_loop()
        self._loop_out = asyncio.new_event_loop()

        self._agent_manager = AgentManager(engine=self)
        self._client_manager = ClientManager(engine=self)

        self._engine_manager_thread = EngineManagerThread(self._loop)
        self._engine_manager_thread.start()
        self._engine_manager_futures = []

        self._engine_manager_output_thread = EngineManagerThread(
            self._loop_out
        )  # no multithreading in python
        self._engine_manager_output_thread.start()
        self._engine_manager_output_futures = []

    def get_loop(self):
        return self._loop

    def get_output_loop(self):
        return self._loop_out

    def _find_client_queue_(self, client_id) -> ClientQueue:
        for ctq in self._all_queues:
            if ctq.client._id == client_id:
                return ctq.client_queue

        return None

    def _find_client_to_queue_(self, client_id):
        for ctq in self._all_queues:
            if ctq.client._id == client_id:
                return ctq

        return None

    def clear_queues(self):
        self._all_queues = []

    def add_client(self, client: Client):
        cl = self._find_client_queue_(client._id)

        if cl is not None:
            return

        client.add_engine(self)
        client_queue = ClientQueue(client)
        agent_queue = None

        ctq = ClientToQueues(client, client_queue, agent_queue)

        self._all_queues.append(ctq)

    def add_agent(self, client: Client, agent: Agent = None):
        ctq = self._find_client_to_queue_(client._id)

        if ctq is None or agent is None:
            return

        agent.add_engine(self)
        ctq.agents.append(agent)
        aq = AgentQueue(agent)
        ctq.agent_queue = aq

    def remove_client(self, client: Client):
        self._all_queues = list(
            filter(lambda ctq: (ctq.client._id != client._id), self._all_queues)
        )

    def add_message(self, client_id, input):
        ctq = self._find_client_to_queue_(client_id)

        if ctq is not None:
            ctq.client_queue.add_message(input)

        self._engine_manager_futures.append(
            asyncio.run_coroutine_threadsafe(self.process(), self._loop)
        )

    def add_agent_output(self, client_id, input):
        ctq = self._find_client_to_queue_(client_id)

        if ctq is not None:
            ctq.agent_queue.add_message(input)

        self._engine_manager_output_futures.append(
            asyncio.run_coroutine_threadsafe(self.output(), self._loop_out)
        )

    async def process(self):
        for ctq in self._all_queues:
            if ctq.client_queue._is_new:
                await self._agent_manager.to_process(ctq)

    async def output(self):
        for ctq in self._all_queues:
            if ctq.agent_queue._is_new:
                await self._client_manager.to_process(ctq)

    def quit(self):
        if self._agent_manager is not None:
            self._agent_manager.quit()
