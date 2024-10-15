import traceback
import uuid


class Agent:
    def __init__(self, engine=None):
        self._id = uuid.uuid4().hex
        self.engine = engine

    def add_engine(self, engine):
        self.engine = engine

    def process(self, client_id, client_msg):
        try:
            # return self.agent_executor.invoke({"input": client_msg})
            return (client_id, 200)
        except Exception as e:
            print(e.__traceback__)
            print(traceback.format_exc())
