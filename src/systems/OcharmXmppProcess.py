from multiprocessing import Process, Queue
import json
import traceback

from .OcharmXmppBot import OcharmXmppBot


class OcharmXmppProcess(Process):
    def __init__(self, in_queue: Queue, out_queue: Queue, jid, password):
        super(OcharmXmppProcess, self).__init__()

        self.bot = OcharmXmppBot(jid, password, self.on_message)
        self.in_queue = in_queue
        self.out_queue = out_queue

        self.bot.register_plugin('xep_0030')  # Service Discovery
        self.bot.register_plugin('xep_0004')  # Data Forms
        self.bot.register_plugin('xep_0060')  # PubSub
        self.bot.register_plugin('xep_0199')  # XMPP Ping

        self.bot.connect()

    def run(self):
        # self.bot.process(forever=False)

        try:
            while True:
                self.bot.process(forever=False)
                msg = self.in_queue.get()

                obj = json.loads(msg)

                match obj['type']:
                    case 'ocharm_process_quit':
                        break
                    case 'message':
                        self.bot.send_message(obj['to'], obj['msg'])
        except Exception as e:
            print("OcharmXmppProcess Exception")
            traceback.print_exc()

    def on_message(self, message):
        self.out_queue.put(message)
