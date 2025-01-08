
import slixmpp


class OcharmXmppMessage(slixmpp.ClientXMPP):

    def __init__(self, jid, password, recipient, message):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.recipient = recipient
        self.msg = message

        self.add_event_handler("session_start", self.start)

    async def start(self, event):

        self.send_presence()
        await self.get_roster()

        self.send_message(mto=self.recipient,
                          mbody=self.msg,
                          mtype='chat')

        self.disconnect()
