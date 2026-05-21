import json
import asyncio
from typing import Dict, List
from fastapi import WebSocket
from app.core.redis import get_redis

class ConnectionManager:
    def __init__(self):
        # Local mapping of room ID to list of WebSockets connected on this instance
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Keep track of background tasks for listening to redis
        self.pubsub_tasks: Dict[str, asyncio.Task] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
            # Make sure we are subscribed to this room on Redis
            await self._subscribe_to_room(room_id)
        
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            try:
                self.active_connections[room_id].remove(websocket)
            except ValueError:
                pass
            if not self.active_connections[room_id]:
                # If no more local users in this room, clean up and unsubscribe
                del self.active_connections[room_id]
                self._unsubscribe_from_room(room_id)

    async def broadcast_to_room(self, room_id: str, message: dict):
        """
        Publishes the message to Redis. The pubsub listener will pick it up
        and distribute it to all active local WebSocket connections.
        """
        redis_client = get_redis()
        if redis_client:
            await redis_client.publish(f"chat:{room_id}", json.dumps(message))

    async def _subscribe_to_room(self, room_id: str):
        redis_client = get_redis()
        if not redis_client:
            return
            
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(f"chat:{room_id}")

        async def _listen():
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    await self._send_to_local_sockets(room_id, data)

        task = asyncio.create_task(_listen())
        self.pubsub_tasks[room_id] = task

    def _unsubscribe_from_room(self, room_id: str):
        if room_id in self.pubsub_tasks:
            self.pubsub_tasks[room_id].cancel()
            del self.pubsub_tasks[room_id]

    async def _send_to_local_sockets(self, room_id: str, message: dict):
        if room_id in self.active_connections:
            dead_sockets = []
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    dead_sockets.append(connection)
            
            # Clean up dead sockets
            for dead in dead_sockets:
                self.disconnect(dead, room_id)

manager = ConnectionManager()
