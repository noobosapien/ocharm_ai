from multiprocessing import Process, Queue
import json
import time
import traceback

from .task_sort import task_sort


class Scheduler(Process):
    def __init__(self, in_queue: Queue, out_queue: Queue):
        super(Scheduler, self).__init__()

        self.in_queue = in_queue
        self.out_queue = out_queue

        self.all_tasks = []
        self.pending_tasks = []

    def run(self):
        try:
            while True:
                if not self.in_queue.empty():

                    new_msg = self.in_queue.get()
                    msg_obj = json.loads(new_msg)

                    match msg_obj["type"]:
                        case 1:
                            # create/add
                            msg_obj["type"] = "sched_task"
                            self.all_tasks.append(msg_obj)
                            # sort the list
                            self.sort_all_tasks()

                        case 2:
                            # next task
                            obj = {"type": "sched_next_task",
                                   "next_task": self.all_tasks[0]}
                            self.out_queue.put(json.dumps(obj))
                            pass
                        case 3:
                            # update
                            pass
                        case 4:
                            # delete
                            pass
                        case 5:
                            # finished task
                            pass
                        case 6:
                            # no of tasks
                            obj = {"type": "sched_len",
                                   "length": len(self.all_tasks)}
                            self.out_queue.put(json.dumps(obj))

                        case 'q':
                            break
                        case _:
                            pass

                for task in self.all_tasks:
                    now_ts = time.time()

                    if 'timestamp' in task and now_ts > task['timestamp']:
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
        task_sort(self.all_tasks)
