from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.mongodb import ChatRoomSchema, ChatMessageSchema
from app.core.mongodb import get_mongodb
from app.services.websocket import manager

router = APIRouter()

class RoomCreate(BaseModel):
    name: str

@router.post("/rooms", response_model=ChatRoomSchema)
async def create_room(
    room_in: RoomCreate,
    current_user: User = Depends(get_current_active_user),
    db_mongo = Depends(get_mongodb)
) -> Any:
    room = ChatRoomSchema(
        name=room_in.name,
        room_type="group",
        participants=[current_user.id],
        created_by=current_user.id
    )
    result = await db_mongo["chat_rooms"].insert_one(
        room.model_dump(by_alias=True, exclude={"id"})
    )
    room.id = str(result.inserted_id)
    return room

@router.get("/rooms", response_model=List[ChatRoomSchema])
async def get_rooms(
    current_user: User = Depends(get_current_active_user),
    db_mongo = Depends(get_mongodb)
) -> Any:
    cursor = db_mongo["chat_rooms"].find({"participants": current_user.id, "is_active": True})
    rooms = await cursor.to_list(length=100)
    return rooms

@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    # In a real scenario, you authenticate via token passed in URL params or protocol here.
    # For now, we accept directly.
    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Send message to Redis PubSub to broadcast to all clients in this room scaleably
            await manager.broadcast_to_room(room_id, {
                "message": data,
                "room": room_id
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
