from datetime import datetime, timedelta
import json
import traceback
from modules.component import Component


class Task(Component):
    def __init__(self,
                 uid: str = None,
                 description: str = None,
                 severity: int = None,
                 minute: int = None,
                 hour: int = None,
                 day: int = None,
                 month: int = None,
                 year: int = None):
        self.uid: str = uid
        self.description: str = description
        self.severity: int = severity
        self.minute: int = minute
        self.hour: int = hour
        self.day: int = day
        self.month: int = month
        self.year: int = year
        self.completed: bool = False
        self.notified: int = 0

        if year and month and day and hour and minute:
            ct = datetime(year, month, day, hour, minute, 0, 0)
            self.timestamp = ct.timestamp()

            next_minute = 0

            if self.severity == 1:
                next_minute = 3
            elif self.severity == 2:
                next_minute = 2
            else:
                next_minute = 1

            ct_next = ct + timedelta(minutes=next_minute)
            self.next_timestamp = ct_next.timestamp()
        else:
            self.timestamp = None
            self.next_timestamp = None

    def from_json(self, uid, task):

        print('task: ', task)

        try:
            self.uid = uid
            self.description = task['description']
            self.severity = task['severity']
            self.minute = task['minute']
            self.hour = task['hour']
            self.day = task['day']
            self.month = task['month']
            self.year = task['year']
            self.completed = False
            self.notified = task['notified']

            if self.year and self.month and self.day and self.hour and self.minute:
                ct = datetime(self.year, self.month, self.day,
                              self.hour, self.minute, 0, 0)
                self.timestamp = ct.timestamp()

                next_minute = 0

                if self.severity == 1:
                    next_minute = 3
                elif self.severity == 2:
                    next_minute = 2
                else:
                    next_minute = 1

                ct_next = ct + timedelta(minutes=next_minute)
                self.next_timestamp = ct_next.timestamp()

            else:
                self.timestamp = None
                self.next_timestamp = None

        except Exception as e:
            print("Exception occured at creating a task from json")
            traceback.print_exc()

    def set_completed(self, completed: bool):
        self.completed = completed

    def serialize(self):
        to_ret = {}

        if self.uid:
            to_ret['uid'] = self.uid

        if self.timestamp:
            to_ret['timestamp'] = self.timestamp

        if self.next_timestamp:
            to_ret['next_timestamp'] = self.next_timestamp

        if self.description:
            to_ret['description'] = self.description

        if self.severity:
            to_ret['severity'] = self.severity

        if self.minute:
            to_ret['minute'] = self.minute

        if self.hour:
            to_ret['hour'] = self.hour

        if self.day:
            to_ret['day'] = self.day

        if self.month:
            to_ret['month'] = self.month

        if self.year:
            to_ret['year'] = self.year

        to_ret['notified'] = self.notified

        return to_ret
