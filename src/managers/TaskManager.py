from multiprocessing import Queue
import json

from classes.Task import Task

from .Scheduler import Scheduler


class TaskManager:
    def __init__(self, callback):
        self.next_task = None

        self.callback = callback

        self.queue_to_sched = Queue()
        self.queue_to_tm = Queue()

        self.scheduler = Scheduler(self.queue_to_sched, self.queue_to_tm)

        # self.scheduler.daemon = True
        self.scheduler.start()

    def add_task(self, task: Task):
        obj = task.serialize()
        obj["type"] = 1
        task_json = json.dumps(obj)
        self.queue_to_sched.put(task_json)

        refresh = {'type': 2}
        refresh_json = json.dumps(refresh)
        self.queue_to_sched.put(refresh_json)

    def poll_due_event(self):
        if self.queue_to_tm.empty():
            return None
        else:
            return self.queue_to_tm.get()

    def complete_task(self, task_id):
        pass

    def get_next_task(self):
        return self.next_task

    def set_next_task(self, task):
        self.next_task = task

    def get_queue_empty(self):
        obj = {}
        obj["type"] = 6
        obj_json = json.dumps(obj)
        self.queue_to_sched.put(obj_json)

    def process(self, message):
        match message:
            case 'int_next_task':
                obj = {}
                obj["type"] = 2
                obj_json = json.dumps(obj)
                self.queue_to_sched.put(obj_json)
            case _:
                pass

    def quit(self):
        obj = {}
        obj["type"] = 'q'
        obj_json = json.dumps(obj)
        self.queue_to_sched.put(obj_json)
        self.scheduler.join()
