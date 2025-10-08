"""
WebSocket connection manager
"""

from typing import List
from fastapi import WebSocket
import logging
import json

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("New WebSocket connection established")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info("WebSocket connection disconnected")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Failed to send personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected WebSockets"""
        disconnected_connections = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Failed to broadcast message: {e}")
                disconnected_connections.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected_connections:
            self.disconnect(connection)
    
    async def broadcast_json(self, data: dict):
        """Broadcast JSON data to all connected WebSockets"""
        message = json.dumps(data)
        await self.broadcast(message)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()