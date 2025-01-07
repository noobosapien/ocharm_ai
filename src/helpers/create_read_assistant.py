
from modules.OcharmReadAgent import OcharmReadAgent

from tools.read_tools import (hof_get_next_task, GetNextTask)


def create_read_assistant(engine, client, task_manager):
    agent = OcharmReadAgent(
        content="You are an assistant who can read from existing tasks in the system, try to infer what is asked from the input\n"
        "and call the certain functions to show the result.\n"
        "For example:\n"
        "What is the next task that should be done?\n"
        "call 'GetNextTask' tool with args:\n"
        "output=True\n",
        engine=engine,
        task_manager=task_manager,
    )

    agent.add_tool(
        hof_get_next_task,
        GetNextTask,
        name="GetNextTask",
        description="Get information of the next task to complete.",
        client=client,
    )

    return agent
