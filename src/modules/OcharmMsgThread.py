import time
from threading import Thread
from multiprocessing import Queue
from queue import Queue as nQueue
import traceback
import json

from engine.piedpiper_engine import Engine
from engine.core.client import Client
from helpers.create_classifier_assistant import create_classifier_assistant


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

        self.agent_queue = nQueue()

    def callback(self):
        pass

    def run(self):
        try:
            while True:
                msg = self.queue_to_thread.get()
                # self.queue_to_thread.put("recieved message from: " +
                #                    self.jid + " as: " + msg)

                # Classify message
                self.classifier_assistant = create_classifier_assistant(
                    self.engine, self.client, self.agent_queue)

                self.engine.add_agent(self.client, self.classifier_assistant)

                self.engine.add_message(self.client.get_id(), msg)

                time.sleep(3)

                msg = self.agent_queue.get()

                self.engine.remove_agent(
                    self.client, agent=self.classifier_assistant)

                # Authenticate
                get_user_obj = {'type': 'get_user', 'jid': self.jid}
                self.queue_to_main.put(json.dumps(get_user_obj))

                get_user_json = self.queue_to_thread.get()
                user = json.loads(get_user_json)

                print("User: ", user)

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

                    case 2:
                        obj = {"type": "message",
                               "to": self.jid,
                               "msg": "I'm looking for the task."}
                        self.queue_to_main.put(json.dumps(obj))

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
