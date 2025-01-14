from pydantic.v1 import BaseModel, Field

from classes.classified_msg import ClassifiedMSG


def hof_previous_task(agent, client):
    def previous_task(content):
        msg_queue = agent.get_msg_queue()
        msg = ClassifiedMSG(user_id=client.get_id(),
                            content=content, classification=1)

        msg_queue.put(msg)

        return True

    return previous_task


def hof_no_of_tasks(agent, client):
    def no_of_tasks(content):
        msg_queue = agent.get_msg_queue()
        msg = ClassifiedMSG(user_id=client.get_id(),
                            content=content, classification=2)

        msg_queue.put(msg)

        return True

    return no_of_tasks


def hof_next_task(agent, client):
    def next_task(content):
        msg_queue = agent.get_msg_queue()
        msg = ClassifiedMSG(user_id=client.get_id(),
                            content=content, classification=3)

        msg_queue.put(msg)

        return True

    return next_task


def hof_search_task(agent, client):
    def search_task(content):
        msg_queue = agent.get_msg_queue()
        msg = ClassifiedMSG(user_id=client.get_id(),
                            content=content, classification=4)

        msg_queue.put(msg)

        return True

    return search_task


def hof_unknown(agent, client):
    def unknown(content):
        msg_queue = agent.get_msg_queue()
        msg = ClassifiedMSG(user_id=client.get_id(),
                            content=content, classification=5)

        msg_queue.put(msg)

        return True

    return unknown


class Msg(BaseModel):
    content: str = Field(
        description="The content of the message given by the client")
