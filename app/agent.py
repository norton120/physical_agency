from datetime import datetime, timedelta
from openai import OpenAI as Together

from app.settings import settings
from app.logger import get_logger
from app.models.schemas import Message
from app.stubs import tools, system_message # temporary stub

class Agent:

    heartbeat: "datetime"
    heartbeat_interval: int = 10

    def __init__(self):
        self.heartbeat = datetime.now()
        # manage this later
        self.system = Message(role="system", content=system_message)
        self.llm = Together(
            base_url = "https://api.together.xyz/v1",
            api_key=settings.together_api_key)
        self.logger = get_logger(__name__)
        self.messages = [Message(role="assistant", content="Hello! I'm your assistant. How can I help you today?"),
                         Message(role="user", content="I don't need anything thank you good bye.")
                         ]

    def daemon(self):
        while "Processing Heartbeat":
            if datetime.now() >= self.heartbeat:
                self.logger.debug("Heartbeat at %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                messages, tool_calls = self.generate()
                self.logger.debug(f"Messages: {messages}")
                self.logger.debug(f"Tool Calls: {tool_calls}")
                if tool_calls:
                    _ = [self.execute_tool_call(tool_call) for tool_call in tool_calls]
                if messages:
                    _ = [self.enqueue_assistant_message(message) for message in messages]
                self.heartbeat = datetime.now() + timedelta(seconds=self.heartbeat_interval)

    def generate(self):
        # send the current context window to the LLM
        # get back messages and function calls
        # return messages and function calls
        messages = [self.system.model_dump(exclude_none=True)] + [message.model_dump(exclude_none=True) for message in self.messages]
        response = self.llm.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=messages,
            tool_choice="auto",
            tools=tools
        )
        messages, tool_calls = [], []
        for choice in response.choices:
            if tool_call := choice.message.tool_calls:
                tool_calls += tool_call
            if content := choice.message.content:
                messages.append(Message(role="assistant", content=content))
        return messages, tool_calls

    def execute_tool_call(self, tool_call):
        # TODO: first need to add the function request message to self.messages
        if tool_call.function.name == "message_user":
            self.logger.debug(f"Sending message to user: {tool_call.parameters.content}")
            # TODO: then add the tool response to self.messages
            self.messages.append(Message(role="tool", ))

        if tool_call.function.name == "pause_heartbeat":
            self.logger.debug("Pausing heartbeat")
            self.heartbeat = datetime.now() + timedelta(days=365)
            return
        self.logger.debug(f"Executing tool call: {tool_call}")

    def enqueue_assistant_message(self, message):
        # TODO: this should shift the oldest messages to storage
        self.messages.append(message)