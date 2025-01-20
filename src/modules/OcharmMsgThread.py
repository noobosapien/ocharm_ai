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
    """Thread for each client that messaged the Ocharm, 
    it will run as a state machine for every message recieved after classifying them."""

    def __init__(self, jid: str, queue_to_thread: Queue, queue_to_main: Queue):
        """Initialize the thread by taking the JID of the client, the queue to recieve messages from the main
        and a queue to the main."""
        Thread.__init__(self, daemon=True)

        # The only part of the JID needed is the part with the domain name
        self.jid = jid.split("/")[:][0]

        # Save the queues to self
        self.queue_to_thread = queue_to_thread
        self.queue_to_main = queue_to_main

        # Create an instance of the engine in the thread
        # Because the engine can handle one agent at a time
        self.engine = Engine()
        self.client = Client(self.jid, self.engine, self.callback)

        # Add the client to the engine
        self.engine.add_client(self.client)

        # The types of agents required
        self.classifier_assistant = None
        self.read_classifier_assistant = None

        # TAKE THIS TO THE RELEVANT PLACE OF THE LOOP
        self.agent_queue = nQueue()
        self.task_frame = None

    def callback(self):
        """Callback given to the agents, NOT USED NOW, AGENTS USE QUEUES."""
        pass

    def run(self):
        """The main loop of the thread, keeps running until stop. It works as a state machine.
        Classify a message first and then reclassify the message according to the previous classification
        and the new agent."""
        try:
            while True:
                # Blocks the thread to get the message
                user_msg = self.queue_to_thread.get()

                # Classify message for the first time to check for what the message belongs to
                # in CRUD
                self.classifier_assistant = create_classifier_assistant(
                    self.engine, self.client, self.agent_queue)
                self.engine.add_agent(self.client, self.classifier_assistant)
                self.engine.add_message(self.client.get_id(), user_msg)

                # Get the classified message from the agent queue given to the message by the agent
                # Blocks the thread.
                msg = self.agent_queue.get()

                # After getting the message remove the agent from the engine.
                # So the engine can process the other agents depending on the message
                self.engine.remove_agent(
                    self.client, agent=self.classifier_assistant)

                # Authenticate

                # Get the user object from the database
                get_user_obj = {'type': 'get_user', 'jid': self.jid}
                self.queue_to_main.put(json.dumps(get_user_obj))

                # Block the thread until the next message from the main
                # Which will contain the user object
                get_user_json = self.queue_to_thread.get()
                user = json.loads(get_user_json)

                # If the message cannot be classified into CRUD
                # Send the message to the client saying that the message cannot be understood
                # Go back to the begining of the loop and wait for a new CRUD message
                if msg.classification == 5:
                    obj = {"type": "message",
                           "to": self.jid,
                           "msg": "Sorry I don't understand that task."}
                    self.queue_to_main.put(json.dumps(obj))
                    continue

                # Check whether the user is authorized to process the message
                # If not authorized send a message to the client saying unauthorized
                # And go back to the beginning of the loop and wait for a CRUD message
                if not (user['authenticated_use'] & 1 << msg.classification):
                    obj = {"type": "message",
                           "to": self.jid,
                           "msg": "Sorry you are not authenticated to perform this action."}
                    self.queue_to_main.put(json.dumps(obj))
                    continue

                # Action of the message
                match msg.classification:
                    case 1:
                        # Classification 1 from the agent is to create a task
                        # Notify the client that the task is being created
                        obj = {"type": "message",
                               "to": self.jid,
                               "msg": "I'm creating the task."}
                        self.queue_to_main.put(json.dumps(obj))

                        # Create a frame if one is not already present
                        if self.task_frame is None:
                            self.task_frame = TaskFrame()

                        # Create the agent used to populate the frame and add it to the engine
                        frame_assistant = create_frame_assistant(
                            engine=self.engine, client=self.client, frame=self.task_frame)
                        self.engine.add_agent(self.client, frame_assistant)

                        # Add the message to the engine to populate the frame
                        string = "edit current frame with the user input: " + user_msg
                        self.engine.add_message(
                            client_id=self.client.get_id(), input=string)

                        # Since there are no queues in use for this agent
                        # This is a way to block the thread
                        # TODO: Use a queue instead of sending in the frame
                        time.sleep(2)
                        while self.engine.get_process_list_len() != 0:
                            time.sleep(1)

                        # If the frame has information missing
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

                            # Send a message to the client to fill in the missing values of the frame required to
                            # create a task.
                            message = f"Please enter the missing values for:"
                            for value in missing:
                                message += ' ' + value + ','

                            message = message[:-1] + '.'

                            obj = {"type": "message",
                                   "to": self.jid,
                                   "msg": message}
                            self.queue_to_main.put(json.dumps(obj))

                            # Block the thread until the message is recieved by the client
                            user_msg = self.queue_to_thread.get()

                            # Create a new message to send to the frame agent to complete the frame
                            string = (
                                f"edit current frame:{
                                    self.task_frame.to_json()} with the user input: "
                                + user_msg
                            )
                            self.engine.add_message(
                                client_id=self.client.get_id(), input=string)

                            # Block the thread until processed
                            # TODO: use a queue instead of sending the frame to the agent
                            time.sleep(2)
                            while self.engine.get_process_list_len() != 0:
                                time.sleep(1)

                            # Check whether the frame is complete
                            # If so this inner loop can be broken
                            self.task_frame.check_complete()

                        # TODO: Remove this line
                        self.task_frame.complete = True  # use check_complete

                        # If the frame is complete
                        # send the json of the frame to the main to create a task
                        # and add it to the task manager
                        if self.task_frame.is_complete():
                            task = self.task_frame.to_task(self.jid)

                            obj = {"type": "create_task",
                                   "to": self.jid,
                                   "msg": task.serialize()}
                            self.queue_to_main.put(json.dumps(obj))

                            self.engine.remove_agent(
                                self.client, agent=frame_assistant)

                            obj = {"type": "message",
                                   "to": self.jid,
                                   "msg": "Sucesfully created the task." + json.dumps(task.serialize())}
                            self.queue_to_main.put(json.dumps(obj))

                        # At the end remove the frame so the next task created will have
                        # No artifacts from the previous task
                        self.task_frame = None

                    case 2:
                        # Classification 2 from the agent is to read a task
                        # Notify the client of finding the task
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

                        # Create a queue for the agent
                        # And create the agent to classify the message even more
                        # In the read class
                        read_queue = nQueue()
                        read_class_assistant = create_read_classifier_assistant(
                            self.engine, self.client, read_queue)

                        self.engine.add_agent(
                            self.client, read_class_assistant)

                        # Add the user's message to the engine
                        self.engine.add_message(self.client.get_id(), user_msg)

                        # Block the thread to get the message from the queue
                        msg = read_queue.get()

                        # Remove the agent from the engine
                        self.engine.remove_agent(
                            self.client, agent=read_class_assistant)

                        # This class of message is the same as the first classification message
                        # It has user_id, classification and content
                        match msg.classification:
                            # Depending on the classification
                            case 1:
                                # Type 1 of the classification is to get the previous task from the
                                # task manager
                                # Send a message to the client saying that the previous task
                                # is being looked up
                                obj = {"type": "message",
                                       "to": self.jid,
                                       "msg": "Wait till I get the previous task."}
                                self.queue_to_main.put(json.dumps(obj))

                                # Send a message to the main - task_manager
                                # Type tm_previous_task is to get the previous task from the task manager
                                obj = {"type": "tm_previous_task",
                                       "to": self.jid}
                                self.queue_to_main.put(json.dumps(obj))

                            case 2:
                                # Type 2 of the classification is to get the number of tasks from the
                                # task manager
                                # Send a message to the client saying that the number of tasks
                                # is being looked up
                                obj = {"type": "message",
                                       "to": self.jid,
                                       "msg": "Wait till I get the number of tasks."}
                                self.queue_to_main.put(json.dumps(obj))

                                # Send a message to the main - task_manager
                                # Type tm_no_of_tasks is to get the number of tasks from the task manager
                                obj = {"type": "tm_no_of_tasks",
                                       "to": self.jid}
                                self.queue_to_main.put(json.dumps(obj))
                                # Wait for the message
                                # Send to the user

                            case 3:
                                # Type 3 of the classification is to get the next task from the
                                # task manager
                                # Send a message to the client saying that the next task
                                # is being looked up
                                obj = {"type": "message",
                                       "to": self.jid,
                                       "msg": "Wait till I get the next task."}
                                self.queue_to_main.put(json.dumps(obj))

                                # Send a message to the main - task_manager
                                # Type tm_next_task is to get the next task from the task manager
                                obj = {"type": "tm_next_task",
                                       "to": self.jid}
                                self.queue_to_main.put(json.dumps(obj))
                                # Wait for the message
                                # Send to the user

                            case 4:
                                # Type 4 of the classification is to search for a task from the
                                # task manager
                                # Send a message to the client saying that the task
                                # is being looked up
                                obj = {"type": "message",
                                       "to": self.jid,
                                       "msg": "I'm sorry I still don't have the capability of searching a task."}
                                self.queue_to_main.put(json.dumps(obj))

                                # Send a message to the main - task_manager

                                # Send to the user
                                # Ask whether it is the correct task?
                                # If not ask for another explanation
                                # Repeat sending and asking
                                # Until correct one is given

                                # 4 -
                                # Fill the task frame with the available information from the input and then
                                # The task frame doesn't have to be complete
                                # Send in to the main queue with the type: "get_task"
                                # Wait for the object from the task manager
                                # If the object is not None send it to the client and ask whether that is the object
                                # classify the answer from the client

                            case 5:
                                # Type 5 of the classification is unknown
                                # Send a message to the client saying that the task is unknown
                                obj = {"type": "message",
                                       "to": self.jid,
                                       "msg": "Sorry I don't know what task you are asking for."}
                                self.queue_to_main.put(json.dumps(obj))

                            case _:
                                # Other classifications are unknown
                                # Send a message to the client saying that the task is unknown
                                obj = {"type": "message",
                                       "to": self.jid,
                                       "msg": "Sorry I don't know what task you are asking for."}
                                self.queue_to_main.put(json.dumps(obj))

                                pass

                    case 3:
                        obj = {"type": "message",
                               "to": self.jid,
                               "msg": "I'm updating the last task."}
                        self.queue_to_main.put(json.dumps(obj))

                        # Right now it can only complete the previous task
                        obj = {"type": "tm_complete_prev_task",
                               "to": self.jid}
                        self.queue_to_main.put(json.dumps(obj))

                    case 4:

                        # TODO: delete after searching a task
                        obj = {"type": "message",
                               "to": self.jid,
                               "msg": "I'm sorry I still don't have the capability of deleting a task."}
                        self.queue_to_main.put(json.dumps(obj))

                    case _:
                        obj = {"type": "message",
                               "to": self.jid,
                               "msg": "Sorry I don't understand that task."}
                        self.queue_to_main.put(json.dumps(obj))

        except Exception as e:
            print("Exception at OcharmMsgThread: ", e)
            traceback.print_exc()
