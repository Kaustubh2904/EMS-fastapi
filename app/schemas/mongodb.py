from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> Any:
        from pydantic_core import core_schema
        return core_schema.str_schema()

class MongoBaseModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class ChatRoomSchema(MongoBaseModel):
    name: Optional[str] = None
    room_type: str = "direct"
    participants: List[int] = []
    created_by: Optional[int] = None
    identifier: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatMessageSchema(MongoBaseModel):
    room_id: str
    sender_id: int
    content: str
    message_type: str = "text"
    parent_message_id: Optional[str] = None
    is_edited: bool = False
    is_deleted: bool = False
    read_by: List[int] = []
    reactions: Dict[str, List[int]] = {}
    file_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ActivityLogSchema(MongoBaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: Optional[int] = None
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    action: str
    method: Optional[str] = None
    endpoint: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    model_name: Optional[str] = None
    object_id: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = {}
