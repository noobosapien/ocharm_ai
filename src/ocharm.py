
import traceback
import os
from multiprocessing import Queue
import json

from dotenv import load_dotenv
from systems.OcharmXmppProcess import OcharmXmppProcess
from modules.OcharmMsgThread import OcharmMsgThread

from classes.Task import Task
from managers.TaskManager import TaskManager
from engine.piedpiper_engine import Engine
from db_connection import SessionLocal
from models import User
import traceback

load_dotenv()


class Ocharm:
    """The main class that will be run with the main loop"""

    def __init__(self):
        """Initialize the class with no arguments.
        It will get JID and the password from the environment.
        Create two multiprocessing queues one towards the xmpp_process and the
        other from the xmpp_process to this.
        Then initialize the xmpp_process, and the task manager
        """
        self.jid = os.environ.get("OCHARM_JID")
        self.password = os.environ.get("OCHARM_PW")

        self.xmpp_in_queue = Queue()
        self.xmpp_out_queue = Queue()

        self.xmpp_process: OcharmXmppProcess = None

        self.engine = Engine()
        self.db = SessionLocal()
        self.task_manager = TaskManager(self.task_due)

        self.client_messages = {}  # JID - Queue
        self.client_threads = {}  # JID - Thread

    def task_due(self, content, hour, minute):
        """The callback function when a task is due. Not currently used."""
        print("Task: ", content, " is due at time: ", hour, ":", minute)

    def send_to_in_queue(self, to, text):
        """Send the text given to this function to the xmpp_process to send to the client provided."""
        obj = {'type': 'message',
               'to': to, 'msg': text}
        self.xmpp_in_queue.put(json.dumps(obj))

    def setup(self):
        """Setup the xmpp_process"""
        try:
            self.xmpp_process = OcharmXmppProcess(
                self.xmpp_in_queue, self.xmpp_out_queue, self.jid, self.password)
            self.xmpp_process.start()
        except Exception as e:
            print(e)
            traceback.print_exc()

    def process(self):
        """Function of the main loop of the class. Running this will block the thread"""
        try:
            while True:
                # If there is a message from the xmpp_procees
                if not self.xmpp_out_queue.empty():
                    # Get the message
                    msg = self.xmpp_out_queue.get()

                    if msg:
                        # Make a python object from the json provided it will be {'from', 'msg'}
                        msg = json.loads(msg)

                        # Send back to the client that the message is being processed
                        self.send_to_in_queue(
                            msg["from"], "I'm processing: \"" + msg['msg'] + "\" please hang on a moment.")

                        # Create two multiprocess queues for the client one each way with the key being the obj['from'] value
                        # One goes to the thread and the other comes from the thread
                        if msg["from"] not in self.client_messages:
                            self.client_messages[msg["from"]] = (
                                Queue(), Queue())  # tuple queue_to_thread, queue_to_main

                        # Put the message from the client to the queue that is going towards the thread.
                        self.client_messages[msg["from"]][0].put(msg['msg'])

                        # Threads are always running.
                        # If there is no thread for the client create a thread and add it to the dictionary.
                        if msg["from"] not in self.client_threads:
                            self.client_threads[msg["from"]] = OcharmMsgThread(
                                msg['from'],
                                self.client_messages[msg["from"]][0],
                                self.client_messages[msg["from"]][1],
                            )

                            self.client_threads[msg["from"]].start()

                # Jid is the key of the client_messages
                # Value is a tuple of Queues for the thread and from the thread
                for jid in self.client_messages:
                    # Get any messages from the client thread to the main
                    msg_queue = self.client_messages[jid][1]  # queue_to_main

                    # Unblock the while loop
                    if not msg_queue.empty():

                        # Get the message and make a dictionary
                        msg = msg_queue.get()
                        obj = json.loads(msg)

                        # Switch the type of the message
                        match obj["type"]:
                            case "message":
                                # If it is of the message type send to the client
                                self.send_to_in_queue(obj["to"], obj['msg'])

                            case "get_user":
                                # Get the user from the database
                                user = self.db.query(User).filter(
                                    User.jid == obj["jid"]).first()

                                user_obj = {'name': None,
                                            'authenticated_use': 0}

                                if user:
                                    user_obj['name'] = user.name
                                    user_obj['authenticated_use'] = user.authenticated_use

                                # Send the information about the database user to the thread
                                self.client_messages[jid][0].put(
                                    json.dumps(user_obj))

                            case 'create_task':
                                # Create a new task and add it to the task manager
                                task = Task()
                                # Populate the task from the object recieved from the thread
                                task.from_json(obj['to'], obj['msg'])
                                self.task_manager.add_task(task)

                            # case 'get_task':
                            #     task_desc = Task()
                            #     task_desc.from_json(obj['to'], obj['msg'])

                            #     task = self.task_manager.get_task(task_desc)

                            case 'tm_previous_task':
                                # Call the function to get the previous task from the task manager
                                # The input from the task manager is not handled here.
                                # It is handled in the next part of the loop
                                self.task_manager.get_previous_task(obj['to'])

                            case 'tm_next_task':
                                # Call the function to get the next task from the task manager
                                # The input from the task manager is not handled here.
                                # It is handled in the next part of the loop
                                self.task_manager.get_next_task(obj['to'])

                            case _:
                                pass

                # If there are events from the task manager get them
                # if there are no events None will be returned
                msg = self.task_manager.poll_due_event()

                # Unblocking if None
                if msg is not None:
                    # Create an object from the message the json comes from the scheduler
                    msg = json.loads(msg)

                    # Switch the type of message from the scheduler
                    # The type always starts from sched
                    match msg['type']:
                        case 'sched_to_client_task_due':
                            # When a task is due
                            self.send_to_in_queue(
                                msg['uid'], "Task due: " + msg['description'])

                        case 'sched_previous_task':
                            # When the previous task is asked for, happens after the function call of the last part of the loop
                            # Send the previous task to the client who asked for it
                            jid = msg['to']

                            if msg['previous_task'] is None:
                                self.send_to_in_queue(
                                    jid, 'There are no previous tasks.')
                            else:
                                self.send_to_in_queue(
                                    jid, json.dumps(msg['previous_task']))

                        case 'sched_next_task':
                            # When the next task is asked for, happens after the function call of the last part of the loop
                            # Send the next task to the client who asked for it
                            print("Next task: ", msg['next_task'])
                            jid = msg['to']

                            if msg['next_task'] is None:
                                self.send_to_in_queue(
                                    jid, 'There are no tasks left.')
                            else:
                                self.send_to_in_queue(
                                    jid, json.dumps(msg['next_task']))

                        case _:
                            pass

        except Exception as e:
            print("Exception at ocharm: ", e)
            traceback.print_exc()

    def quit(self):
        """Quit the xmpp_process after sending it the message to stop the loop."""
        self.xmpp_in_queue.put(json.dumps({'type': 'ocharm_process_quit'}))
        self.xmpp_process.join()


if __name__ == '__main__':
    ocharm = Ocharm()
    ocharm.setup()
    ocharm.process()
