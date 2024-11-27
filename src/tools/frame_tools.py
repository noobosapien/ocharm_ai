from pydantic.v1 import BaseModel, Field
from classes.task_frame import TaskFrame


def hof_set_content(agent, client):
    def set_content(content):
        frame = agent.get_frame()
        frame.set_content(content)

        return True

    return set_content


class Content(BaseModel):
    content: str = Field("A short description of the task")


def hof_set_severity(agent, client):
    def set_severity(severity):
        frame = agent.get_frame()
        frame.set_severity(severity)

        return True

    return set_severity


class Severity(BaseModel):
    severity: int = Field("The severity of a task low = '1', medium = '2', high = '3'")


def hof_set_minute_due(agent, client):
    def set_minute_due(minute_due):
        frame = agent.get_frame()
        frame.set_minute_due(minute_due)

        return True

    return set_minute_due


class Minute_due(BaseModel):
    minute_due: int = Field("The minute value of a certain time between 0 and 59")


def hof_set_hour_due(agent, client):
    def set_hour_due(hour_due):
        frame = agent.get_frame()
        frame.set_hour_due(hour_due)

        return True

    return set_hour_due


class Hour_due(BaseModel):
    hour_due: int = Field("The hour value of a certain time between 0 and 23")


def hof_set_day_due(agent, client):
    def set_day_due(day_due):
        frame = agent.get_frame()
        frame.set_day_due(day_due)

        return True

    return set_day_due


class Day_due(BaseModel):
    day_due: int = Field("The day value of a certain date between 0 and 31")


def hof_set_month_due(agent, client):
    def set_month_due(month_due):
        frame = agent.get_frame()
        frame.set_month_due(month_due)

        return True

    return set_month_due


class Month_due(BaseModel):
    month_due: int = Field("The month value of a certain date between 1 and 12")


def hof_set_year_due(agent, client):
    def set_year_due(year_due):
        frame = agent.get_frame()
        frame.set_year_due(year_due)

        return True

    return set_year_due


class Year_due(BaseModel):
    year_due: int = Field("The year value of a certain date")
