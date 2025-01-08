
from multiprocessing import Process, Queue
import json
import traceback
from threading import Thread

from .OcharmXmppBot import OcharmXmppBot
from .OcharmXmppMessage import OcharmXmppMessage


class OcharmXmppProcess(Process):
    def __init__(self, in_queue: Queue, out_queue: Queue, jid, password):
        super(OcharmXmppProcess, self).__init__()

        self.bot = OcharmXmppBot(jid, password, self.on_message)
        self.jid = jid
        self.password = password

        self.in_queue = in_queue
        self.out_queue = out_queue

        self.bot.register_plugin('xep_0030')  # Service Discovery
        self.bot.register_plugin('xep_0004')  # Data Forms
        self.bot.register_plugin('xep_0060')  # PubSub
        self.bot.register_plugin('xep_0199')  # XMPP Ping

        self.bot.connect()
        self.bot_thread = Thread(target=self.xmpp_process)
        self.bot_thread.start()

    def run(self):

        try:
            while True:
                msg = self.in_queue.get()

                obj = json.loads(msg)

                match obj['type']:
                    case 'ocharm_process_quit':
                        break
                    case 'message':
                        self.xmpp_send_message(obj['to'], obj['msg'])
        except Exception as e:
            print("OcharmXmppProcess Exception")
            traceback.print_exc()

    def xmpp_process(self):
        self.bot.process()

    def on_message(self, message):
        self.out_queue.put(message)

    def xmpp_send_message(self, to, msg):
        xmpp_message = OcharmXmppMessage(
            self.jid, self.password, to, msg)
        xmpp_message.register_plugin('xep_0030')
        xmpp_message.register_plugin('xep_0199')

        xmpp_message.connect()
        xmpp_message.process(forever=False)
