import json
from .Task import Task


class TaskFrame:
    def __init__(self):
        self.complete = False
        self.content = None
        self.severity = None

        self.minute_due = None
        self.hour_due = None

        self.day_due = None
        self.month_due = None
        self.year_due = None

        self.timestamp = None

    def check_complete(self):
        self.complete = (
            self.content is not None
            and self.severity is not None
            and self.minute_due is not None
            and self.hour_due is not None
            and self.day_due is not None
            and self.month_due is not None
            and self.year_due is not None
        )

    def set_content(self, content):
        self.content = content

    def set_severity(self, severity):
        self.severity = severity

    def set_minute_due(self, minute_due):
        self.minute_due = minute_due

    def set_hour_due(self, hour_due):
        self.hour_due = hour_due

    def set_day_due(self, day_due):
        self.day_due = day_due

    def set_month_due(self, month_due):
        self.month_due = month_due

    def set_year_due(self, year_due):
        self.year_due = year_due

    def is_complete(self):
        return self.complete

    def to_task(self, uid) -> Task:
        task = Task(uid=uid,
                    description=self.content,
                    severity=self.severity,
                    minute=self.minute_due,
                    hour=self.hour_due,
                    day=self.day_due,
                    month=self.month_due,
                    year=self.year_due)

        return task

    def to_json(self):
        obj = {}

        obj["content"] = self.content
        obj["severity"] = self.severity
        obj["minute_due"] = self.minute_due
        obj["hour_due"] = self.hour_due
        obj["day_due"] = self.day_due
        obj["month_due"] = self.month_due
        obj["year_due"] = self.year_due
        obj["complete"] = self.complete

        return json.dumps(obj)
