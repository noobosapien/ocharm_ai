from pydantic.v1 import BaseModel, Field
from ..engine.core.agent import Agent
from ..engine.core.client import Client

def hof_create_task(agent: Agent = None, client: Client = None):
    def create_task(name, description, severity, minute, hour, day, month, year):

        return True

    return create_task

class CreateTask(BaseModel):
    name: str = Field(description="Task name with a few meaningful words")
    
    description:str = Field(
        description="A short description of the task specified"
    )
    
    severity: int = Field(
        description="Severity of the task 1 - low, 2 - medium, 3 - high, choose from the 3 integers"
    )
    
    minute: int = Field(
        description="The minute the task has to be completed from 0 to 59"
    ) 
    
    hour: int = Field(
        description="The hour the task has to be completed from 0 to 23"
    )
    
    day: int = Field(
        description="The day of the month the task has to be completed"
    )
    
    month: int = Field(
        description="The month the task has to be completed"
    )
    
    year: int = Field(
        description="The year the task has to be completed"
    )