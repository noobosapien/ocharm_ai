from pydantic.v1 import BaseModel, Field


def hof_get_next_task(agent, client):
    def get_next_task(output=False):
        task_manager = agent.get_task_manager()
        task = task_manager.get_next_task()

        if output:
            print("Task from read_tools: ", task)

        return task

    return get_next_task


class GetNextTask(BaseModel):
    output: bool = Field(
        "True to show the output or False to not show the output of the task")
