from multiprocessing import Process, Queue
import json
import time


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
                            del msg_obj["type"]
                            self.all_tasks.append(msg_obj)
                        case 2:
                            # read
                            pass
                        case 3:
                            # update
                            pass
                        case 4:
                            # delete
                            pass
                        case _:
                            pass

                for task in self.all_tasks:
                    now_ts = time.time()

                    if now_ts > task["timestamp"]:
                        self.out_queue.put(json.dumps(task))
                        self.pending_tasks.append(task)

                        self.remove_from_sll_tasks(task)

        except Exception as e:
            print("Exception occured: ", e)

    def remove_from_sll_tasks(self, task):
        self.all_tasks = filter(
            lambda t: not (
                t["timestamp"] == task["timestamp"] and t["description"] == task["description"]),
            self.all_tasks)
