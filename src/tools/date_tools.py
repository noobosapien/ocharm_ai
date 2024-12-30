from pydantic.v1 import BaseModel, Field
import time
from engine.core.agent import Agent
from engine.core.client import Client


def hof_current_time_and_date(agent: Agent = None, client: Client = None):
    def current_time_and_date():

        return f"Current date and time: {time.ctime()}"

    return current_time_and_date


class CurrentDateTime(BaseModel):
    pass
