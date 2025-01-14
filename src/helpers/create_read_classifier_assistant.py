from modules.OcharmMSGtypeAgent import OcharmMSGtypeAgent

from tools.read_classifier_tools import (  # noqa: E402
    Msg,
    hof_next_task,
    hof_no_of_tasks,
    hof_previous_task,
    hof_search_task,
    hof_unknown
)


def create_read_classifier_assistant(engine, client, msg_queue):
    classifier_assistant = OcharmMSGtypeAgent(
        content="You are an assistant who classifies a message depending on contents as:\n"
        "Get previous task, get next task, Get number of tasks, Search for task, Unknown\n"
        "CALL THE RELEVANT TOOLS WITH THE SAME MESSAGE SENT TO YOU.\n"
        "For example:\n"
        "'What was the last task I had to complete?'\n"
        "call get_previous_task tool with args:\n"
        "content='What was the last task I had to complete?'\n"
        "Another example:\n"
        "'What is the next task I must complete?'\n"
        "call the get_next_task tool with args:\n"
        "content='What is the next task I must complete?'"
        "Another example:\n"
        "'What are is the task at 7pm?'"
        "call the search_for_task tool with args:\n"
        "content='What are is the task at 7pm?'"
        "Another example:\n"
        "'Give me the task about medicine'\n"
        "call the search_for_task tool with args:\n"
        "content='Give me the task about medicine'",
        engine=engine,
        msg_queue=msg_queue,
    )

    classifier_assistant.add_tool(
        hof_previous_task,
        Msg,
        "get_previous_task",
        "Create an instance of message with the type 'Previous Task' depending on the contents of the client messsage asking about the previous task.",
        client,
    )

    classifier_assistant.add_tool(
        hof_next_task,
        Msg,
        "get_next_task",
        "Create an instance of message with the type 'Next Task' depending on the contents of the client messsage asking about the next task to complete.",
        client,
    )

    classifier_assistant.add_tool(
        hof_no_of_tasks,
        Msg,
        "get_number_of_tasks",
        "Create an instance of message with the type 'Number of Tasks' depending on the contents of the client messsage\n"
        "asking about the number of tasks to complete.",
        client,
    )

    classifier_assistant.add_tool(
        hof_search_task,
        Msg,
        "search_for_task",
        "Create an instance of message with the type 'Search for Task' depending on the contents of the client messsage\n"
        "given either a description or time of a task.",
        client,
    )

    classifier_assistant.add_tool(
        hof_unknown,
        Msg,
        "unknown",
        "Create an instance of message with the type 'Unknown' depending on the contents of the client messsage, and if you can't decide whether"
        "it belongs to one of Previous message/Number of tasks/Next task/Search task",
        client,
    )

    return classifier_assistant
