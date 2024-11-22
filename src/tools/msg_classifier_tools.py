
from pydantic.v1 import BaseModel, Field

from classes.ClassifiedMSG import ClassifiedMSG 


def hof_create_msg(agent, client):
    def create_msg(
        content
    ):
        msg_queue= agent.get_msg_queue()
        msg = ClassifiedMSG(user_id=client.get_id(), content=content, classification=1)
        msg_queue.push(msg)

        return True

    return create_msg

def hof_read_msg(agent, client):
    def read_msg(
        content
    ):
        msg_queue= agent.get_msg_queue()
        msg = ClassifiedMSG(user_id=client.get_id(), content=content, classification=2)
        msg_queue.push(msg)

        return True

    return read_msg

def hof_update_msg(agent, client):
    def update_msg(
        content
    ):
        msg_queue= agent.get_msg_queue()
        msg = ClassifiedMSG(user_id=client.get_id(), content=content, classification=3)
        msg_queue.push(msg)

        return True

    return update_msg

def hof_delete_msg(agent, client):
    def delete_msg(
        content
    ):
        msg_queue= agent.get_msg_queue()
        msg = ClassifiedMSG(user_id=client.get_id(), content=content, classification=4)
        msg_queue.push(msg)

        return True

    return delete_msg


class Msg(BaseModel):
    content: str = Field(description="The content of the message given by the client")
    