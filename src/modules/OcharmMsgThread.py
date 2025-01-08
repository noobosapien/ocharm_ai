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
    def __init__(self, jid: str, queue: Queue):
        Thread.__init__(self, daemon=True)

        self.jid = jid.split("/")[:][0]
        self.msg_queue = queue
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
                msg = self.msg_queue.get()
                # self.msg_queue.put("recieved message from: " +
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

                print(msg.classification, msg.user_id, msg.content)

                # Action of the message

                match msg.classification:
                    case 1:
                        pass

                    case _:
                        obj = {"type": "message",
                               "to": self.jid,
                               "msg": "Sorry I don't understand that task."}
                        self.msg_queue.put(json.dumps(obj))

        except Exception as e:
            print("Exception at OcharmMsgThread: ", e)
            traceback.print_exc()
