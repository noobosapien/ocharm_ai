import asyncio
import functools
from concurrent.futures import ThreadPoolExecutor


class ClientManager:
    def __init__(self, engine=None):
        self._engine = engine
        self.loop = engine.get_output_loop()
        self.tasks = []

    def clear_finished_tasks(self):
        self.tasks = list(
            filter(
                lambda task: (task.done() is False),
                self.tasks,
            )
        )

    async def to_process(self, ctq):
        with ThreadPoolExecutor() as pool:
            while ctq.agent_queue.is_empty() is False:
                self.tasks.append(
                    self.loop.run_in_executor(
                        pool,
                        functools.partial(
                            ctq.client.output,
                            ctq.agent_queue.get_next_message(),
                        ),
                    )
                )

            for result in asyncio.as_completed(self.tasks):
                self.clear_finished_tasks()
                await result
                # self._engine.dec_running()

    def quit(self):
        # self.agent_processor.cancel_all()
        pass
