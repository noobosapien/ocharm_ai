from multiprocessing import Queue
import json

from classes.Task import Task

from .Scheduler import Scheduler


class TaskManager:
    """The class that manages all the tasks done by the users"""

    def __init__(self, callback):
        """Initializes the task manager with the callback function to call when a task is due, NOT CURRENTLY USED.
        The task manager gets messages from the poll_due_events and returns the result to the caller.
        All the tasks are kept in the scheduler.
        This contact the scheduler and asks for tasks that are queried."""
        self.callback = callback

        # Create two queues one towards the scheduler and the other towards this.
        self.queue_to_sched = Queue()
        self.queue_to_tm = Queue()

        # Create the scheduler and start it.
        self.scheduler = Scheduler(self.queue_to_sched, self.queue_to_tm)
        self.scheduler.start()

    def add_task(self, task: Task):
        """Add a task to the scheduler. Since it is another process serialize the task into a json object
        before sending it through to the scheduler."""
        obj = task.serialize()

        # Type for adding an object to the scheduler is tm_sched_add_task
        obj["type"] = 'tm_sched_add_task'
        task_json = json.dumps(obj)
        # Send to the scheduler
        self.queue_to_sched.put(task_json)

    def get_previous_task(self, to):
        """Get the previous task of the user and send the JID as the to variable.
        The result will be from polling for events"""

        # Type of the object for the previous task is tm_sched_get_prev
        get_prev = {'type': 'tm_sched_get_prev', 'to': to}
        get_prev_json = json.dumps(get_prev)
        self.queue_to_sched.put(get_prev_json)

    def get_next_task(self, to):
        """Get the next task of the user and send the JID as the to variable.
        The result will be from polling for events"""

        # The type of the object for getting the next task is tm_sched_get_next
        get_next = {'type': 'tm_sched_get_next', 'to': to}
        get_next_json = json.dumps(get_next)
        self.queue_to_sched.put(get_next_json)

    def poll_due_event(self):
        """Gets events from the scheduler and returns to the caller.
        If there are no events from the scheduler, returns None."""
        if self.queue_to_tm.empty():
            return None
        else:
            return self.queue_to_tm.get()

    # def get_queue_empty(self):
    #     obj = {}
    #     obj["type"] = 6
    #     obj_json = json.dumps(obj)
    #     self.queue_to_sched.put(obj_json)

    # def process(self, message):
    #     match message:
    #         case 'int_next_task':
    #             obj = {}
    #             obj["type"] = 2
    #             obj_json = json.dumps(obj)
    #             self.queue_to_sched.put(obj_json)
    #         case _:
    #             pass

    def quit(self):
        """Send the message to the scheduler to stop the loop and quit."""
        obj = {}
        obj["type"] = 'q'
        obj_json = json.dumps(obj)
        self.queue_to_sched.put(obj_json)
        self.scheduler.join()
