import traceback
from typing import Any
from uuid import UUID

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.callbacks.base import BaseCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               MessagesPlaceholder)
from langchain.schema import SystemMessage
from langchain.tools import StructuredTool
from langchain_core.messages import BaseMessage
from langchain_openai.chat_models import ChatOpenAI

from core.agent import Agent
from modules.timeline import Timeline


class ChatModelStartHandler(BaseCallbackHandler):
    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[BaseMessage]],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        return super().on_chat_model_start(
            serialized,
            messages,
            run_id=run_id,
            parent_run_id=parent_run_id,
            tags=tags,
            metadata=metadata,
            **kwargs,
        )


class LangchainSyncAgent(Agent):
    def __init__(self, content, engine=None):
        super().__init__(engine)
        self.timeline = Timeline()  # temp
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

    def get_timeline(self):
        return self.timeline

    def add_tool(self, hof, args_schema, name, description):
        tool_func = hof(self)

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
        self.agent = create_openai_functions_agent(
            llm=self.chat,
            tools=self.tools,
            prompt=self.prompt,
        )

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            verbose=False,
            tools=self.tools,
            memory=self.memory,
        )

    def process(self, client_id, input):
        try:
            self.agent_executor.invoke({"input": input})
            return (client_id, self.timeline)

        except Exception as e:
            print(e.__traceback__)
            print(traceback.format_exc())
