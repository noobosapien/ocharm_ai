
from pydantic.v1 import BaseModel, Field

from .placetime import Placetime


def hof_create_place_time(agent):
    def create_place_time(
        place="", place_vague=True, time="", date="", time_vague=True
    ):
        timeline = agent.get_timeline()
        pt = Placetime()

        timeline.addPlacetime(pt)

        pt1: Placetime = timeline.getPlacetime(0)
        pt1.createPlace(place, place_vague)
        pt1.createTime(time, date, time_vague)

        return True

    return create_place_time


class CreatePlaceTime(BaseModel):
    place: str = Field(description="place name")
    place_vague: bool = Field(
        description="whether the place is vague determined by whethe the given place has a name or a general description"
    )
    time: str | None = Field(
        description="time of the event only of given otherwise nothing"
    )
    date: str = Field(
        description="date as described could be specific if it can be calculated or general if it cannot be calculated"
    )
    time_vague: bool = Field(
        description="whether the date is vague depending on whether the date can be calculated if it can be calculated it is not vague"
    )
