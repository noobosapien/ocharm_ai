import json

import slixmpp


class OcharmXmppBot(slixmpp.ClientXMPP):

    def __init__(self, jid, password, callback):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)

        self.callback = callback

    async def start(self, event):
        self.send_presence()
        await self.get_roster()

    def message(self, msg):
        # self.send_message("migara@xmpp.jp", "A new message", "chat")
        if msg['type'] in ('chat', 'normal'):
            obj = {"from": str(msg['from']), "msg": msg['body']}
            self.callback(json.dumps(obj))
            # msg.reply("Thanks for sending\n%(body)s" % msg).send()
