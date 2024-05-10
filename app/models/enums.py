from enum import Enum

class MessageRole(str, Enum):
    """the classic OAI compatible message Role"""
    assistant:str = "assistant"
    user:str = "user"
    system:str = "system"
    tool:str = "tool"