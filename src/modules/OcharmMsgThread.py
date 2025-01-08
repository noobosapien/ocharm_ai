from threading import Thread
from multiprocessing import Queue


class OcharmMsgThread(Thread):
    def __init__(self, jid: str, queue: Queue):
        Thread.__init__(self, daemon=True)

        self.jid = jid
        self.msg_queue = queue

    def run(self):
        while True:
            msg = self.msg_queue.get()
            self.msg_queue.put("recieved message from: " +
                               self.jid + " as: " + msg)

            # Classify message
            # Action of the message
