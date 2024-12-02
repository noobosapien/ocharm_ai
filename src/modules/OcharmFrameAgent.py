import traceback

from engine.core.agent import Agent
from .MessageHandler import ChatModelStartHandler


from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.callbacks.base import BaseCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from langchain.tools import StructuredTool
from langchain_openai.chat_models import ChatOpenAI


class OcharmFrameAgent(Agent):
    def __init__(self, content, engine=None, frame=None):
        super().__init__(engine)

        self.frame = frame
        self.tools = []
        self.agent = None

        self.handler = ChatModelStartHandler()
        self.chat = ChatOpenAI(model="gpt-4o-mini", callbacks=[self.handler])

        self.prompt = ChatPromptTemplate(
            messages=[
                SystemMessage(content=content),
                MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        self.memory = ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        )

    def get_frame(self):
        return self.frame

    def add_tool(self, hof, args_schema, name, description, client):
        tool_func = hof(self, client)

        self.tools.append(
            StructuredTool.from_function(
                name=name,
                description=description,
                func=tool_func,
                args_schema=args_schema,
            )
        )

        self.update_agent()

    def update_agent(self):
        print(self.tools)
        self.agent = create_openai_functions_agent(
            llm=self.chat,
            tools=self.tools,
            prompt=self.prompt,
        )

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            verbose=True,
            tools=self.tools,
            memory=self.memory,
        )

    def process(self, client_id, input):
        try:
            self.agent_executor.invoke({"input": input})
            return (client_id, self.msg_queue)

        except Exception as e:
            print(e.__traceback__)
            print(traceback.format_exc())
