from .component import Component


class Place:
    def __init__(self, name=None, vague=True):
        self.name = name
        self.vague = vague


class Time:
    def __init__(self, time=None, date=None, vague=True):
        self.time = time
        self.date = date
        self.vague = vague


class Placetime(Component):
    def __init__(self):
        self.uid = None
        self.place = None
        self.time = None

        self.entities = []
        self.actions = []
        self.statements = []

    def createPlace(self, name, vague):
        self.place = Place(name, vague)

    def createTime(self, time=None, date=None, vague=True):
        self.time = Time(time, date, vague)

    def addEntity(self, entity):
        self.entities.append(entity)

    def addAction(self, action):
        self.actions.append(action)

    def addStatement(self, statement):
        self.statements.append(statement)

    def serialize(self):
        to_ret = {}

        if self.time:
            to_ret["time"] = {}

            if self.time.time:
                to_ret["time"]["time"] = self.time.time
            if self.time.date:
                to_ret["time"]["date"] = self.time.date

            to_ret["time"]["vague"] = self.time.vague

        if self.place:
            to_ret["place"] = {}

            if self.place.name:
                to_ret["place"]["name"] = self.place.name

            to_ret["place"]["vague"] = self.place.vague

        to_ret["entities"] = []

        for e in self.entities:
            to_ret["entities"].append(e.serialize())

        to_ret["statements"] = []

        for s in self.statements:
            to_ret["statements"].append(s.serialize())

        to_ret["actions"] = []

        for a in self.actions:
            to_ret["actions"].append(a.serialize())

        return to_ret
