from multiprocessing import Queue
import json

from classes.Task import Task

from .Scheduler import Scheduler


class TaskManager:
    def __init__(self, callback):
        self.next_task = None
        self.all_tasks = []
        self.pending_tasks = []

        self.callback = callback

        self.queue_to_sched = Queue()
        self.queue_to_tm = Queue()

        self.scheduler = Scheduler(self.queue_to_sched, self.queue_to_tm)

        # self.scheduler.daemon = True
        self.scheduler.start()

    def add_task(self, task: Task):
        self.all_tasks.append(task)

        obj = task.serialize()
        obj["type"] = 1
        task_json = json.dumps(obj)
        self.queue_to_sched.put(task_json)

    def poll_due_task(self):
        if self.queue_to_tm.empty():
            return None
        else:
            return self.queue_to_tm.get()

    def complete_task(self, task_id):
        pass

    def get_next_task(self):
        pass

    def quit(self):
        self.scheduler.join()
