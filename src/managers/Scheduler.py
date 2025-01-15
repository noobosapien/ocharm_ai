from multiprocessing import Process, Queue
import json
import time
import traceback

from .task_sort import task_sort


class Scheduler(Process):
    """The class that holds all the pending tasks and tasks yet to be notified.
    The purpose of this class is to send events about tasks with time and when queried.
    This class extends a process as it blocks the runnin thread with a loop."""

    def __init__(self, in_queue: Queue, out_queue: Queue):
        """Initialize with the input queue for this and the output queue for the caller"""
        super(Scheduler, self).__init__()

        self.in_queue = in_queue
        self.out_queue = out_queue

        # The arrays have dictionaries of tasks - not json strings
        self.all_tasks = []
        self.pending_tasks = []

    def run(self):
        """The main loop of the scheduler, it looks for new messages from the caller, processes them, 
        and looks for tasks that have their time due and sends to the caller through the queue."""
        try:
            while True:
                # Non-blocking
                if not self.in_queue.empty():
                    new_msg = self.in_queue.get()

                    # Get the message as an object
                    msg_obj = json.loads(new_msg)

                    # Switch the type of the message
                    match msg_obj["type"]:

                        # Add a task
                        case 'tm_sched_add_task':
                            # Change the type of the task
                            msg_obj["type"] = "sched_task_todo"
                            # Add it to all the tasks
                            self.all_tasks.append(msg_obj)
                            # Sort the tasks, first being the task to notify the soonest and the last been the task to notify the latest
                            # NOT IMPLEMENTED YET
                            self.sort_all_tasks()

                        case 'tm_sched_get_next':
                            # Get the next task
                            next_task = None
                            if len(self.all_tasks) > 0:
                                # Next task is the first task of the list all_tasks after sorting
                                next_task = self.all_tasks[0]
                                next_task["type"] = "sched_next_task"

                            # Send the task to the caller queue with the type sched_next_task
                            obj = {"type": "sched_next_task",
                                   "next_task": next_task,
                                   'to': msg_obj['to']}
                            self.out_queue.put(json.dumps(obj))

                        case 'tm_sched_get_prev':
                           # Get the previous task
                            prev = None
                            if len(self.pending_tasks) > 0:
                                # Next task is the last task of the list pending_tasks
                                prev = self.pending_tasks[len(
                                    self.pending_tasks) - 1]
                                prev["type"] = "sched_previous_task"

                            # Send the task to the caller queue with the type sched_prev_task
                            obj = {"type": "sched_previous_task",
                                   "previous_task": prev,
                                   'to': msg_obj['to']}
                            self.out_queue.put(json.dumps(obj))

                        case 'q':
                            # Quit the loop
                            break
                        case _:
                            pass

                # After processing the in_queue, look for all the tasks
                # If any of them are due send it to the out_queue for notifying the client.
                for task in self.all_tasks:
                    now_ts = time.time()

                    if 'timestamp' in task and now_ts > task['timestamp']:
                        task['type'] = 'sched_to_client_task_due'
                        self.out_queue.put(json.dumps(task))
                        self.pending_tasks.append(task)

                        self.remove_from_all_tasks(task)

                for task in self.pending_tasks:
                    # if the pending task is not completed after a certain time
                    # notify the relevant parties

                    pass

        except Exception as e:
            print("Scheduler Exception occured: ", e)
            traceback.print_exc()

    def remove_from_all_tasks(self, task):
        try:
            self.all_tasks = list(filter(
                lambda t: not (
                    t["timestamp"] == task["timestamp"] and t["description"] == task["description"]),
                self.all_tasks))
        except Exception as e:
            print("Remove from all tasks exception: ", e)

    def sort_all_tasks(self):
        # task_sort(self.all_tasks)
        pass
