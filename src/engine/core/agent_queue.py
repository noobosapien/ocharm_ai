

class AgentQueue:
    def __init__(self, agent):
        self._messages: list[str] = []
        self._agent = agent
        self._is_new = True

    def is_agent(self, agent):
        return agent._id == self._agent._id

    def is_agent_by_id(self, agent_id):
        return agent_id == self._agent._id

    def get_agent_id(self):
        return self._agent._id

    def add_message(self, input):
        self._messages.append(input)
        self._is_new = True

    def get_next_message(self):
        if len(self._messages) > 0:
            message = self._messages[0]
            self._messages.pop(0)
            self._is_new = False
            return message
        self._is_new = False
        return None

    def is_empty(self):
        return len(self._messages) == 0

    def get_length(self):
        return len(self._messages)
