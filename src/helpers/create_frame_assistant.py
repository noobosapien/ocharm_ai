from modules.OcharmFrameAgent import OcharmFrameAgent
from tools.frame_tools import (
    hof_set_content,
    hof_set_severity,
    hof_set_minute_due,
    hof_set_hour_due,
    hof_set_day_due,
    hof_set_month_due,
    hof_set_year_due,
    Content,
    Severity,
    Minute_due,
    Hour_due,
    Day_due,
    Month_due,
    Year_due,
)


def create_frame_assistant(engine, client, frame):
    agent = OcharmFrameAgent(
        content="You are an assistant who changes values of an instance of a frame to create a task the fields on the frame are.\n"
        "content, severity, minute_due, hour_due, day_due, month_due, year_due, and complete.\n"
        "try to fill all the fields from the input, if you cannot fill all the fields leave them blank.\n"
        "CALL THE RELEVANT TOOLS WITH THE RELEVANT ARGUMENTS.\n"
        "For example:\n",
        engine=engine,
        frame=frame,
    )

    agent.add_tool(
        hof_set_content,
        Content,
        name="Contents",
        description="Contents of the task frame, which is a short description of the task",
        client=client,
    )

    agent.add_tool(
        hof_set_severity,
        Severity,
        name="Severity",
        description="Severity of the task frame, which is taken only by the user input and it is an integer form 1 to 3",
        client=client,
    )

    agent.add_tool(
        hof_set_minute_due,
        Minute_due,
        name="Minute due",
        description="The value of the minute of the time that task is to be completed",
        client=client,
    )

    agent.add_tool(
        hof_set_hour_due,
        Hour_due,
        name="Hour due",
        description="The value of the hour of the time that task is to be completed",
        client=client,
    )

    agent.add_tool(
        hof_set_day_due,
        Day_due,
        name="Day due",
        description="The value of the day of the date that task is to be completed",
        client=client,
    )

    agent.add_tool(
        hof_set_month_due,
        Month_due,
        name="Month due",
        description="The value of the month of the date that task is to be completed",
        client=client,
    )

    agent.add_tool(
        hof_set_year_due,
        Year_due,
        name="Year due",
        description="The value of the year of the date that task is to be completed",
        client=client,
    )

    return agent
