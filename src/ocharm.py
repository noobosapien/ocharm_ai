
import traceback
import os
from multiprocessing import Queue
import json

from dotenv import load_dotenv
from systems.OcharmXmppProcess import OcharmXmppProcess
from modules.OcharmMsgThread import OcharmMsgThread

from engine.core.client import Client
from classes.task_frame import TaskFrame
from helpers.create_frame_assistant import create_frame_assistant
from helpers.create_classifier_assistant import create_classifier_assistant
from helpers.create_read_assistant import create_read_assistant
from managers.TaskManager import TaskManager
from engine.piedpiper_engine import Engine
from db_connection import get_db_session, SessionLocal
from models import User
import time
import traceback

load_dotenv()


class Ocharm:
    def __init__(self):
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
        print("Task: ", content, " is due at time: ", hour, ":", minute)

    def client_callback(user_id: str, output: str) -> None:
        print(user_id, ": ", output, "\n\n\n")

    def create_client(self, jid):
        client = Client(id=jid, callback=self.client_callback)
        self.engine.add_client(client)

    def send_to_in_queue(self, msg, text):
        obj = {'type': 'message',
               'to': msg["from"], 'msg': text}
        self.xmpp_in_queue.put(json.dumps(obj))

    def setup(self):
        try:
            self.xmpp_process = OcharmXmppProcess(
                self.xmpp_in_queue, self.xmpp_out_queue, self.jid, self.password)
            self.xmpp_process.start()
        except Exception as e:
            print(e)
            traceback.print_exc()

    def process(self):
        try:
            while True:
                if not self.xmpp_out_queue.empty():
                    msg = self.xmpp_out_queue.get()

                    if msg:
                        msg = json.loads(msg)

                        self.send_to_in_queue(
                            msg, "I'm processing: \"" + msg['msg'] + "\" please hang on a moment.")

                        if msg["from"] not in self.client_messages:
                            self.client_messages[msg["from"]] = Queue()

                        self.client_messages[msg["from"]].put(msg['msg'])

                        # threads are always running
                        if msg["from"] not in self.client_threads:
                            self.client_threads[msg["from"]] = OcharmMsgThread(
                                msg['from'],
                                self.client_messages[msg["from"]])

                            self.client_threads[msg["from"]].start()

                for jid in self.client_messages:
                    msg_queue = self.client_messages[jid]

                    if not msg_queue.empty():
                        print(msg_queue.get())

        except Exception as e:
            print("Exception at ocharm: ", e)
            traceback.print_exc()

    def quit(self):
        self.xmpp_in_queue.put(json.dumps({'type': 'ocharm_process_quit'}))
        self.xmpp_process.join()


if __name__ == '__main__':
    ocharm = Ocharm()
    ocharm.setup()
    ocharm.process()
