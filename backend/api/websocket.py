"""
WebSocket manager for real-time event streaming to React clients.
"""
import json
import asyncio
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections and broadcasts."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"[WS] Client connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"[WS] Client disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Send message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.active_connections.remove(conn)
    
    async def send_event(self, event_data: dict):
        await self.broadcast({"type": "event", "payload": event_data})
    
    async def send_anomaly(self, anomaly_data: dict):
        await self.broadcast({"type": "anomaly", "payload": anomaly_data})
    
    async def send_agent_update(self, agent_data: dict):
        await self.broadcast({"type": "agent_update", "payload": agent_data})
    
    async def send_safebox_update(self, safebox_data: dict):
        await self.broadcast({"type": "safebox", "payload": safebox_data})


# Global manager instance
manager = ConnectionManager()


@router.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
