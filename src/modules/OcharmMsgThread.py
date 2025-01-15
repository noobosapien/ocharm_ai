from threading import Thread
from multiprocessing import Queue
from queue import Queue as nQueue
import traceback
import json
import time

from engine.piedpiper_engine import Engine
from engine.core.client import Client
from helpers.create_classifier_assistant import create_classifier_assistant
from helpers.create_read_classifier_assistant import create_read_classifier_assistant
from helpers.create_frame_assistant import create_frame_assistant
from classes.task_frame import TaskFrame


class OcharmMsgThread(Thread):
    def __init__(self, jid: str, queue_to_thread: Queue, queue_to_main: Queue):
        Thread.__init__(self, daemon=True)

        self.jid = jid.split("/")[:][0]
        self.queue_to_thread = queue_to_thread
        self.queue_to_main = queue_to_main

        self.engine = Engine()
        self.client = Client(self.jid, self.engine, self.callback)
        self.engine.add_client(self.client)

        self.classifier_assistant = None
        self.read_classifier_assistant = None

        self.agent_queue = nQueue()

        self.task_frame = None

    def callback(self):
        pass

    def run(self):
        try:
            while True:
                user_msg = self.queue_to_thread.get()

                # Classify message
                self.classifier_assistant = create_classifier_assistant(
                    self.engine, self.client, self.agent_queue)

                self.engine.add_agent(self.client, self.classifier_assistant)

                self.engine.add_message(self.client.get_id(), user_msg)

                msg = self.agent_queue.get()

                self.engine.remove_agent(
                    self.client, agent=self.classifier_assistant)

                # Authenticate
                get_user_obj = {'type': 'get_user', 'jid': self.jid}
                self.queue_to_main.put(json.dumps(get_user_obj))

                get_user_json = self.queue_to_thread.get()
                user = json.loads(get_user_json)

                if msg.classification == 5:
                    obj = {"type": "message",
                           "to": self.jid,
                           "msg": "Sorry I don't understand that task."}
                    self.queue_to_main.put(json.dumps(obj))
                    continue

                if not (user['authenticated_use'] & 1 << msg.classification):
                    obj = {"type": "message",
                           "to": self.jid,
                           "msg": "Sorry you are not authenticated to perform this action."}
                    self.queue_to_main.put(json.dumps(obj))
                    continue

                # Action of the message
                match msg.classification:
                    case 1:
                        obj = {"type": "message",
                               "to": self.jid,
                               "msg": "I'm creating the task."}
                        self.queue_to_main.put(json.dumps(obj))

                        if self.task_frame is None:
                            self.task_frame = TaskFrame()

                        frame_assistant = create_frame_assistant(
                            engine=self.engine, client=self.client, frame=self.task_frame)

                        self.engine.add_agent(self.client, frame_assistant)

                        string = "edit current frame with the user input: " + user_msg
                        self.engine.add_message(
                            client_id=self.client.get_id(), input=string)

                        time.sleep(2)
                        while self.engine.get_process_list_len() != 0:
                            time.sleep(1)

                        while (
                            self.task_frame.severity == -1
                            or self.task_frame.minute_due == -1
                            or self.task_frame.hour_due == -1
                            or self.task_frame.day_due == -1
                            or self.task_frame.month_due == -1
                            or self.task_frame.year_due == -1
                        ):
                            missing = []

                            if self.task_frame.severity == -1:
                                missing.append("Severity")

                            if self.task_frame.minute_due == -1:
                                missing.append("Minute")

                            if self.task_frame.hour_due == -1:
                                missing.append("Hour")

                            if self.task_frame.day_due == -1:
                                missing.append("Day")

                            if self.task_frame.month_due == -1:
                                missing.append("Month")

                            if self.task_frame.year_due == -1:
                                missing.append("Year")

                            message = f"Please enter the missing values for: {
                                missing}\n"

                            obj = {"type": "message",
                                   "to": self.jid,
                                   "msg": message}
                            self.queue_to_main.put(json.dumps(obj))

                            user_msg = self.queue_to_thread.get()

                            string = (
                                f"edit current frame:{
                                    self.task_frame.to_json()} with the user input: "
                                + user_msg
                            )
                            self.engine.add_message(
                                client_id=self.client.get_id(), input=string)

                            time.sleep(2)
                            while self.engine.get_process_list_len() != 0:
                                time.sleep(1)

                            print(self.task_frame.to_json())
                            self.task_frame.check_complete()

                        self.task_frame.complete = True  # use check_complete

                        if self.task_frame.is_complete():

                            task = self.task_frame.to_json()

                            obj = {"type": "create_task",
                                   "to": self.jid,
                                   "msg": task}
                            self.queue_to_main.put(json.dumps(obj))

                            self.engine.remove_agent(
                                self.client, agent=frame_assistant)

                            obj = {"type": "message",
                                   "to": self.jid,
                                   "msg": "Sucesfully created the task." + task}
                            self.queue_to_main.put(json.dumps(obj))

                        # at the end
                        self.task_frame = None

                    case 2:
                        obj = {"type": "message",
                               "to": self.jid,
                               "msg": "I'm looking for the task."}
                        self.queue_to_main.put(json.dumps(obj))

                        # Classify the message again
                        # New classifications are
                        # 1 - What was the previous task?
                        # 2 - How many tasks are there at a certain time?
                        # 3 - What is the next task?
                        # 4 - Is there a task like the one explained with description and/or time?

                        read_queue = nQueue()

                        read_class_assistant = create_read_classifier_assistant(
                            self.engine, self.client, read_queue)

                        self.engine.add_agent(
                            self.client, read_class_assistant)

                        self.engine.add_message(self.client.get_id(), user_msg)

                        msg = read_queue.get()

                        self.engine.remove_agent(
                            self.client, agent=read_class_assistant)

                        match msg.classification:
                            case 1:
                                obj = {"type": "message",
                                       "to": self.jid,
                                       "msg": "Wait till I get the previous task."}
                                self.queue_to_main.put(json.dumps(obj))

                                # Send a message to the main - task_manager
                                obj = {"type": "tm_previous_task",
                                       "to": self.jid}

                                self.queue_to_main.put(json.dumps(obj))

                            case 2:
                                obj = {"type": "message",
                                       "to": self.jid,
                                       "msg": "Wait till I get the number of tasks."}
                                self.queue_to_main.put(json.dumps(obj))

                                # Send a message to the main - task_manager
                                obj = {"type": "tm_no_of_tasks",
                                       "to": self.jid}

                                self.queue_to_main.put(json.dumps(obj))
                                # Wait for the message
                                # Send to the user

                            case 3:
                                obj = {"type": "message",
                                       "to": self.jid,
                                       "msg": "Wait till I get the next task."}
                                self.queue_to_main.put(json.dumps(obj))

                                # Send a message to the main - task_manager
                                obj = {"type": "tm_next_task",
                                       "to": self.jid}

                                self.queue_to_main.put(json.dumps(obj))
                                # Wait for the message
                                # Send to the user

                            case 4:
                                obj = {"type": "message",
                                       "to": self.jid,
                                       "msg": "Wait till I search for the task."}
                                self.queue_to_main.put(json.dumps(obj))

                                # Send a message to the main - task_manager
                                # Wait for the message
                                # Send to the user
                                # Ask whether it is the correct task?
                                # If not ask for another explanation
                                # Repeat sending and asking
                                # Until correct one is given

                            case 5:
                                obj = {"type": "message",
                                       "to": self.jid,
                                       "msg": "Sorry I don't know what task you are asking for."}
                                self.queue_to_main.put(json.dumps(obj))

                            case _:
                                pass

                        # 4 -
                        # Fill the task frame with the available information from the input and then
                        # The task frame doesn't have to be complete
                        # Send in to the main queue with the type: "get_task"
                        # Wait for the object from the task manager
                        # If the object is not None send it to the client and ask whether that is the object
                        # classify the answer from the client

                    case 3:
                        obj = {"type": "message",
                               "to": self.jid,
                               "msg": "I'm updating the task."}
                        self.queue_to_main.put(json.dumps(obj))

                    case 4:
                        obj = {"type": "message",
                               "to": self.jid,
                               "msg": "I'm deleting the task."}
                        self.queue_to_main.put(json.dumps(obj))

                    case _:
                        obj = {"type": "message",
                               "to": self.jid,
                               "msg": "Sorry I don't understand that task."}
                        self.queue_to_main.put(json.dumps(obj))

        except Exception as e:
            print("Exception at OcharmMsgThread: ", e)
            traceback.print_exc()
