from asyncio import AbstractEventLoop
from threading import Thread


class EngineManagerThread(Thread):
    def __init__(self, loop: AbstractEventLoop):
        super().__init__()
        self.loop = loop
        self.daemon = True

    def run(self):
        self.loop.run_forever()
