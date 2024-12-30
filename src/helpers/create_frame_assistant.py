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

from tools.date_tools import hof_current_time_and_date, CurrentDateTime


def create_frame_assistant(engine, client, frame):
    agent = OcharmFrameAgent(
        content="You are an assistant who changes values of an instance of a frame to create a task the fields on the frame are.\n"
        "content, severity, minute_due, hour_due, day_due, month_due, year_due, and complete.\n"
        "try to fill all the fields from the input, if you cannot fill all the fields LEAVE THEM BLANK.\n"
        "CALL THE RELEVANT TOOLS WITH THE RELEVANT ARGUMENTS.\n"
        "For example:\n"
        "Take my medication at 9pm after dinner on 6th of december\n"
        "call 'Contents' tool with args:\n"
        "Take medication\n"
        "call 'Severity' tool with args:\n"
        "0\n"
        "call 'MinuteDue' tool with args:\n"
        "0\n"
        "call 'HourDue' tool with args:\n"
        "21\n"
        "call 'DayDue' tool with args:\n"
        "6\n"
        "call 'MonthDue' tool with args:\n"
        "12\n"
        "call 'YearDue' tool with args:\n"
        "-1\n"
        "Another example where the date is not mentioned:\n"
        "Go to the store to buy some snacks at 11:40 am with low priority\n"
        "call 'CurrentDateAndTime' tool to get the current date and time because the date is not mentioned to get the date\n"
        "call 'DayDue' tool with args:\n"
        "result from the call to the tool 'CurrentDateAndTime'"
        "call 'MonthDue' tool with args:\n"
        "result from the call to the tool 'CurrentDateAndTime'"
        "call 'YearDue' tool with args:\n"
        "result from the call to the tool 'CurrentDateAndTime'"
        "call 'MinuteDue' tool with args:\n"
        "40\n"
        "call 'HourDue' tool with args:\n"
        "11\n"
        "call 'Contents' tool with args:\n"
        "Go to store and buy some snacks\n"
        "call 'Severity' tool with args:\n"
        "1\n",
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
        description="Severity of the task frame, which is taken only by the user input and it is an integer form 1 to 3, IMPORTANT: IF THE VALUE IS NOT PRESENT IN THE INPUT RETURN -1",
        client=client,
    )

    agent.add_tool(
        hof_set_minute_due,
        Minute_due,
        name="MinuteDue",
        description="The value of the minute of the time that task is to be completed, IMPORTANT: IF THE VALUE IS NOT PRESENT IN THE INPUT RETURN -1",
        client=client,
    )

    agent.add_tool(
        hof_set_hour_due,
        Hour_due,
        name="HourDue",
        description="The value of the hour of the time that task is to be completed, IMPORTANT: IF THE VALUE IS NOT PRESENT IN THE INPUT RETURN -1",
        client=client,
    )

    agent.add_tool(
        hof_set_day_due,
        Day_due,
        name="DayDue",
        description="The value of the day of the date that task is to be completed, IMPORTANT: IF THE VALUE IS NOT PRESENT IN THE INPUT RETURN -1",
        client=client,
    )

    agent.add_tool(
        hof_set_month_due,
        Month_due,
        name="MonthDue",
        description="The value of the month of the date that task is to be completed, IMPORTANT: IF THE VALUE IS NOT PRESENT IN THE INPUT RETURN -1",
        client=client,
    )

    agent.add_tool(
        hof_set_year_due,
        Year_due,
        name="YearDue",
        description="The value of the year of the date that task is to be completed, IMPORTANT: IF THE VALUE IS NOT PRESENT IN THE INPUT RETURN -1",
        client=client,
    )

    agent.add_tool(
        hof_current_time_and_date,
        CurrentDateTime,
        name="CurrentDateAndTime",
        description="Get the date and time of the system at this moment. IMPORTANT: USE THIS TOOL TO ALWAYS GET THE CURRENT TIME WHEN NEEDED DO NOT MAKE ASSUMPTIONS",
        client=client
    )

    return agent
