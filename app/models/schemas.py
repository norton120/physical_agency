from typing import Optional
from pydantic import BaseModel, field_serializer

from app.models.enums import MessageRole

class Message(BaseModel):
    """the classic OAI compatible message"""
    role: MessageRole
    name: Optional[str] = None
    content: str

    @field_serializer('role')
    def serialize_role(self, role: MessageRole, _info):
        return role.value

class AvailableTool(BaseModel):
    """a tool that is available to the agent"""
    name: str
    description: str
    function: str