"""
WebSocket Manager for real-time communication and push notifications
"""

import asyncio
import json
import logging
import uuid
from typing import Dict, List, Optional, Any
from fastapi import WebSocket
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket) -> str:
        """Accept WebSocket connection and return connection ID"""
        await websocket.accept()
        
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        self.connection_metadata[connection_id] = {
            "connected_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "message_count": 0
        }
        
        logger.info(f"WebSocket connection established: {connection_id}")
        return connection_id
    
    def disconnect(self, connection_id: str):
        """Remove WebSocket connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        if connection_id in self.connection_metadata:
            del self.connection_metadata[connection_id]
        
        logger.info(f"WebSocket connection closed: {connection_id}")
    
    async def send_personal_message(self, connection_id: str, message: Any):
        """Send message to specific connection"""
        if connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                
                # Convert message to JSON if needed
                if isinstance(message, dict):
                    message_str = json.dumps(message)
                else:
                    message_str = str(message)
                
                await websocket.send_text(message_str)
                
                # Update metadata
                if connection_id in self.connection_metadata:
                    self.connection_metadata[connection_id]["last_activity"] = datetime.utcnow().isoformat()
                    self.connection_metadata[connection_id]["message_count"] += 1
                
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
                # Remove broken connection
                self.disconnect(connection_id)
    
    async def broadcast(self, message: Any, exclude_connections: Optional[List[str]] = None):
        """Broadcast message to all connections"""
        exclude_connections = exclude_connections or []
        
        # Convert message to JSON if needed
        if isinstance(message, dict):
            message_str = json.dumps(message)
        else:
            message_str = str(message)
        
        disconnected_connections = []
        
        for connection_id, websocket in self.active_connections.items():
            if connection_id not in exclude_connections:
                try:
                    await websocket.send_text(message_str)
                    
                    # Update metadata
                    if connection_id in self.connection_metadata:
                        self.connection_metadata[connection_id]["last_activity"] = datetime.utcnow().isoformat()
                        self.connection_metadata[connection_id]["message_count"] += 1
                        
                except Exception as e:
                    logger.error(f"Error broadcasting to {connection_id}: {e}")
                    disconnected_connections.append(connection_id)
        
        # Clean up broken connections
        for connection_id in disconnected_connections:
            self.disconnect(connection_id)
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict]:
        """Get connection metadata"""
        return self.connection_metadata.get(connection_id)
    
    def list_connections(self) -> Dict[str, Dict]:
        """List all active connections with metadata"""
        return self.connection_metadata.copy()


class WebSocketManager:
    """Enhanced WebSocket manager with room support and message queuing"""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.rooms: Dict[str, List[str]] = {}  # room_id -> [connection_ids]
        self.connection_rooms: Dict[str, List[str]] = {}  # connection_id -> [room_ids]
        self.message_queue: Dict[str, List[Dict]] = {}  # connection_id -> [messages]
        self.notification_handlers: Dict[str, callable] = {}
    
    async def connect(self, websocket: WebSocket) -> str:
        """Connect WebSocket and return connection ID"""
        return await self.connection_manager.connect(websocket)
    
    def disconnect(self, connection_id: str):
        """Disconnect WebSocket and clean up rooms"""
        # Remove from all rooms
        if connection_id in self.connection_rooms:
            for room_id in self.connection_rooms[connection_id]:
                self.leave_room(connection_id, room_id)
            del self.connection_rooms[connection_id]
        
        # Clear message queue
        if connection_id in self.message_queue:
            del self.message_queue[connection_id]
        
        # Disconnect from connection manager
        self.connection_manager.disconnect(connection_id)
    
    async def send_personal_message(self, connection_id: str, message: Dict[str, Any]):
        """Send message to specific connection with queueing support"""
        
        # Add timestamp and message ID
        enhanced_message = {
            **message,
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "connection_id": connection_id
        }
        
        # Try to send immediately
        if connection_id in self.connection_manager.active_connections:
            await self.connection_manager.send_personal_message(connection_id, enhanced_message)
        else:
            # Queue message for later delivery
            if connection_id not in self.message_queue:
                self.message_queue[connection_id] = []
            
            self.message_queue[connection_id].append(enhanced_message)
            logger.info(f"Queued message for connection {connection_id}")
    
    async def send_to_room(self, room_id: str, message: Dict[str, Any], exclude_connection: Optional[str] = None):
        """Send message to all connections in a room"""
        
        if room_id not in self.rooms:
            logger.warning(f"Room {room_id} not found")
            return
        
        # Add room context to message
        enhanced_message = {
            **message,
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "room_id": room_id
        }
        
        # Send to all connections in room
        for connection_id in self.rooms[room_id]:
            if connection_id != exclude_connection:
                await self.send_personal_message(connection_id, enhanced_message)
    
    def join_room(self, connection_id: str, room_id: str):
        """Add connection to room"""
        if room_id not in self.rooms:
            self.rooms[room_id] = []
        
        if connection_id not in self.rooms[room_id]:
            self.rooms[room_id].append(connection_id)
        
        if connection_id not in self.connection_rooms:
            self.connection_rooms[connection_id] = []
        
        if room_id not in self.connection_rooms[connection_id]:
            self.connection_rooms[connection_id].append(room_id)
        
        logger.info(f"Connection {connection_id} joined room {room_id}")
    
    def leave_room(self, connection_id: str, room_id: str):
        """Remove connection from room"""
        if room_id in self.rooms and connection_id in self.rooms[room_id]:
            self.rooms[room_id].remove(connection_id)
            
            # Remove empty rooms
            if not self.rooms[room_id]:
                del self.rooms[room_id]
        
        if connection_id in self.connection_rooms and room_id in self.connection_rooms[connection_id]:
            self.connection_rooms[connection_id].remove(room_id)
        
        logger.info(f"Connection {connection_id} left room {room_id}")
    
    async def broadcast_notification(self, notification_type: str, data: Dict[str, Any]):
        """Broadcast notification to all connections"""
        
        notification = {
            "type": "notification",
            "notification_type": notification_type,
            "data": data,
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.connection_manager.broadcast(notification)
    
    async def send_push_notification(
        self, 
        target_type: str, 
        target_id: str, 
        notification: Dict[str, Any]
    ):
        """Send push notification based on target type"""
        
        enhanced_notification = {
            **notification,
            "type": "push_notification",
            "target_type": target_type,
            "target_id": target_id,
            "message_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if target_type == "connection":
            await self.send_personal_message(target_id, enhanced_notification)
        elif target_type == "room":
            await self.send_to_room(target_id, enhanced_notification)
        elif target_type == "broadcast":
            await self.connection_manager.broadcast(enhanced_notification)
        else:
            logger.warning(f"Unknown notification target type: {target_type}")
    
    async def deliver_queued_messages(self, connection_id: str):
        """Deliver queued messages when connection is re-established"""
        
        if connection_id in self.message_queue:
            queued_messages = self.message_queue[connection_id]
            
            for message in queued_messages:
                await self.send_personal_message(connection_id, {
                    **message,
                    "queued": True,
                    "delivered_at": datetime.utcnow().isoformat()
                })
            
            # Clear queue after delivery
            del self.message_queue[connection_id]
            logger.info(f"Delivered {len(queued_messages)} queued messages to {connection_id}")
    
    def register_notification_handler(self, notification_type: str, handler: callable):
        """Register custom notification handler"""
        self.notification_handlers[notification_type] = handler
        logger.info(f"Registered notification handler for type: {notification_type}")
    
    async def handle_custom_notification(self, notification_type: str, data: Dict[str, Any]):
        """Handle custom notification with registered handler"""
        
        if notification_type in self.notification_handlers:
            try:
                await self.notification_handlers[notification_type](data)
            except Exception as e:
                logger.error(f"Error in notification handler for {notification_type}: {e}")
        else:
            logger.warning(f"No handler registered for notification type: {notification_type}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket manager statistics"""
        
        total_queued_messages = sum(len(queue) for queue in self.message_queue.values())
        
        return {
            "active_connections": self.connection_manager.get_connection_count(),
            "active_rooms": len(self.rooms),
            "total_queued_messages": total_queued_messages,
            "registered_handlers": len(self.notification_handlers),
            "connections_with_queued_messages": len(self.message_queue),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_room_info(self, room_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific room"""
        
        if room_id not in self.rooms:
            return None
        
        return {
            "room_id": room_id,
            "connection_count": len(self.rooms[room_id]),
            "connections": self.rooms[room_id],
            "created_at": datetime.utcnow().isoformat()  # This should be tracked properly
        }
    
    def list_rooms(self) -> Dict[str, Dict[str, Any]]:
        """List all active rooms"""
        
        return {
            room_id: {
                "connection_count": len(connections),
                "connections": connections
            }
            for room_id, connections in self.rooms.items()
        }
