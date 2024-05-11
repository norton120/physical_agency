from typing import Literal, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path
from openai import OpenAI as Together
from langfuse.decorators import observe, langfuse_context

from app.settings import settings
from app.logger import get_logger
from app.models.schemas import Message, ToolCallResponseMessage
from app.stubs import autonomic_tools, conscious_tools # temporary stub

class Agent:

    heartbeats: dict["datetime"] = {}
    heartbeat_interval: int = 10

    def __init__(self):
        for thought_process in ["conscious", "autonomic"]:
            self.heartbeats[thought_process] = datetime.now()
        # TODO: manage this for real
        seed_prompts = Path("/src/app/seed_prompts")
        conscious = seed_prompts / "firmware" / "conscious.txt"
        autonomic = seed_prompts / "firmware" / "autonomic.txt"
        core = seed_prompts / "core_memory.txt"
        self.conscious_system = [Message(role="system", content=conscious.read_text()),
                                 Message(role="system", content=core.read_text())]
        self.autonomic_system = [Message(role="system", content=autonomic.read_text())]

        self.llm = Together(
            base_url = "https://api.together.xyz/v1",
            api_key=settings.together_api_key)
        self.logger = get_logger(__name__)
        self.messages = [
                         ToolCallResponseMessage(role="assistant", tool_calls=[
                                {"id": "call_04wx09n6j51jmvmh09ugy182",
                                "name": "message_user",
                                "arguments": '{"content": "What doth thou wish to know, Ethan Knox?"}'
                                }

                         ]),
                         Message(role="tool", content="Message successfully sent to user.", tool_call_id="call_04wx09n6j51jmvmh09ugy182"),
                         Message(role="user", name="Ethan Knox", content="My name is Ethan Knox."),
                         Message(role="user", name="Ethan Knox", content="I have no idea how to sail a sailboat."),
                         #Message(role="user", name="Ethan Knox", content="how do you feel about day drinking?"),

                         ]

    def daemon(self, thought_process: Literal["conscious", "autonomic"]):
        while "Processing Heartbeat":
            heartbeat = self.heartbeats[thought_process]
            preprocessed_heartbeat = heartbeat
            if datetime.now() >= heartbeat:
                self.logger.debug("%s Heartbeat at %s", thought_process, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                messages, tool_calls = self.generate(thought_process=thought_process)
                self.logger.debug(f"Messages: {messages}")
                self.logger.debug(f"Tool Calls: {tool_calls}")
                if tool_calls:
                    _ = [self.execute_tool_call(tool_call, thought_process=thought_process) for tool_call in tool_calls]
                if messages:
                    _ = [self.enqueue_assistant_message(message) for message in messages]
                if awake := self.heartbeats[thought_process] == preprocessed_heartbeat:
                    self.logger.info("Updating hearbeat by default interval.")
                    self.heartbeats[thought_process] = datetime.now() + timedelta(seconds=self.heartbeat_interval)
                # if conscious heartbeat is awake, we need to kickstart the autonomic heartbeat if it's asleep
                if thought_process == "conscious" and awake and self.heartbeats["autonomic"] < self.heartbeats["conscious"]:
                    self.logger.info("Agent is awake but autonomic functions are asleep. Difibrillating.")
                    self.heartbeats["autonomic"] = datetime.now()

    @observe()
    def generate(self, thought_process: Literal["conscious", "autonomic"]):
        # send the current context window to the LLM
        # get back messages and function calls
        # return messages and function calls
        match thought_process:
            case "conscious":
                target = self.conscious_system
            case "autonomic":
                target = self.autonomic_system
        messages = [message.model_dump(exclude_none=True) for message in target] + [message.model_dump(exclude_none=True) for message in self.messages]
        tools = autonomic_tools if thought_process == "autonomic" else conscious_tools
        langfuse_context.update_current_trace(metadata={"tools": tools})
        langfuse_context.update_current_observation(
            name = thought_process,
            input = messages,
            start_time=datetime.now(),

        )
        langfuse_context.flush()
        response = self.llm.chat.completions.create(
           model="mistralai/Mistral-7B-Instruct-v0.1",
           #model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=messages,
            tool_choice="auto",
            tools=tools,
            #frequency_penalty=0.4,
        )
        messages, tool_calls = [], []
        for choice in response.choices:
            if tool_call := choice.message.tool_calls:
                tool_calls += tool_call
            if content := choice.message.content:
                messages.append(Message(role="assistant", content=content))
        langfuse_context.update_current_observation(
            end_time=datetime.now(),
        )
        langfuse_context.flush()
        if not any((messages,tool_calls,)):
            self.pause_heartbeat(thought_process)

        return messages, tool_calls

    def execute_tool_call(self, tool_call, thought_process: Literal["conscious", "autonomic"]):
        # TODO: first need to add the function request message to self.messages
        self.logger.info(f"Executing tool call: {tool_call.function.name}")
        self.messages.append(Message(role="assistant", content=f"Execute tool call: {tool_call.model_dump_json(exclude_none=True)}"))
        arguments = json.loads(tool_call.function.arguments or "{}")
        if tool_call.function.name == "message_user":
            self.logger.info(f"Sending message to user: {arguments['content']}")
            # TODO: then add the tool response to self.messages
            self.messages.append(Message(role="tool",
                                         tool_call_id=tool_call.id,
                                         content="Message successfully sent to user."))

        if tool_call.function.name == "remember_about_user":
            self.logger.info("Remembering: %s", arguments)
            self.messages.append(Message(role="tool",
                                         tool_call_id=tool_call.id,
                                         content=f"Information '{arguments['information']}' about '{arguments['user_name']}' successfully remembered."))

        if tool_call.function.name == "go_to_sleep":
            self.pause_heartbeat(thought_process, id_=tool_call.id)

    def pause_heartbeat(self, thought_process: Literal["conscious", "autonomic"], id_:Optional[str] = None):
            self.logger.info("Pausing %s heartbeat", thought_process)
            new_heartbeat = datetime.now() + timedelta(days=365)
            self.heartbeats[thought_process] = new_heartbeat
            if thought_process == "conscious":
                self.messages.append(Message(role="tool",
                                            tool_call_id=id_,
                                            content=f"You executed a function to put yourself to sleep until {new_heartbeat.strftime('%Y-%m-%d %H:%M:%S')}"))

    def enqueue_assistant_message(self, message):
        # TODO: this should shift the oldest messages to storage
        self.messages.append(message)