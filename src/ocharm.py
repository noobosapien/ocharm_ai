import traceback
import os
from multiprocessing import Queue
import json

from dotenv import load_dotenv
from systems.OcharmXmppProcess import OcharmXmppProcess

load_dotenv()

jid = os.environ.get("OCHARM_JID")
password = os.environ.get("OCHARM_PW")

xmpp_in_queue = Queue()
xmpp_out_queue = Queue()

xmpp_process: OcharmXmppProcess = None


def setup():
    try:
        xmpp_process = OcharmXmppProcess(
            xmpp_in_queue, xmpp_out_queue, jid, password)
        xmpp_process.start()
    except Exception as e:
        print(e)
        traceback.print_exc()


def process():
    while True:
        msg = xmpp_out_queue.get()
        print("from xmpp process: ", msg)


def quit():
    xmpp_in_queue.put(json.dumps({'type': 'ocharm_process_quit'}))
    xmpp_process.join()


if __name__ == '__main__':
    setup()
    process()
