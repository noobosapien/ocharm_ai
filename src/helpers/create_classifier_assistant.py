from modules.OcharmMSGtypeAgent import OcharmMSGtypeAgent

from tools.msg_classifier_tools import (  # noqa: E402
    Msg,
    hof_create_msg,
    hof_read_msg,
    hof_update_msg,
    hof_delete_msg,
)


def create_classifier_assistant(engine, client, msg_queue):
    classifier_assistant = OcharmMSGtypeAgent(
        content="You are an assistant who classifies a message depending on contents as Create, Read, Update, and Delete.\n"
        "CALL THE RELEVANT TOOLS WITH THE SAME MESSAGE SENT TO YOU.\n"
        "For example:\n"
        "'Make a task to clean the car in the morning'\n"
        "call create_msg tool with args:\n"
        "content='Make a task to clean the car in the morning'\n"
        "Another example:\n"
        "'Edit the task to call my friend to complete'\n"
        "call the update_msg tool with args:\n"
        "content='Edit the task to call my friend to complete'"
        "Another example:\n"
        "'What is the task at 10am?'"
        "call the read_task tool with args:\n"
        "content='What is the task at 10am?'"
        "Another example:\n"
        "'Remove the task at 11AM'\n"
        "call the delete_task tool with args:\n"
        "content='Remove the task at 11AM'",
        engine=engine,
        msg_queue=msg_queue,
    )

    classifier_assistant.add_tool(
        hof_create_msg,
        Msg,
        "create_message",
        "Create an instance of message with the type 'Create' depending on the contents of the client messsage",
        client,
    )

    classifier_assistant.add_tool(
        hof_read_msg,
        Msg,
        "read_message",
        "Create an instance of message with the type 'Read' depending on the contents of the client messsage",
        client,
    )

    classifier_assistant.add_tool(
        hof_update_msg,
        Msg,
        "update_message",
        "Create an instance of message with the type 'Update' depending on the contents of the client messsage",
        client,
    )

    classifier_assistant.add_tool(
        hof_delete_msg,
        Msg,
        "delete_message",
        "Create an instance of message with the type 'Delete' depending on the contents of the client messsage",
        client,
    )

    return classifier_assistant
