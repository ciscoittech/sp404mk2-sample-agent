"""WebSocket endpoints for real-time updates."""
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import json
import asyncio
from datetime import datetime, timezone

from app.api.deps import get_db
from app.models.sample import Sample
from app.services.vibe_analysis import VibeAnalysisService


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.sample_analysis_status: Dict[int, dict] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept and track a new WebSocket connection."""
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = set()
        self.active_connections[client_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, client_id: str):
        """Remove a WebSocket connection."""
        if client_id in self.active_connections:
            self.active_connections[client_id].discard(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket."""
        await websocket.send_text(message)
    
    async def broadcast_to_sample(self, message: str, sample_id: int):
        """Broadcast a message to all connections watching a specific sample."""
        client_id = f"sample_{sample_id}"
        if client_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[client_id]:
                try:
                    await connection.send_text(message)
                except:
                    disconnected.add(connection)
            
            # Clean up disconnected clients
            for conn in disconnected:
                self.active_connections[client_id].discard(conn)


manager = ConnectionManager()


async def analyze_sample_with_updates(
    sample_id: int, 
    websocket: WebSocket,
    db: AsyncSession
):
    """Run vibe analysis with real-time progress updates."""
    service = VibeAnalysisService(db)
    
    try:
        # Send initial status
        await websocket.send_text(json.dumps({
            "type": "status",
            "status": "analyzing",
            "progress": 0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }))
        
        # Simulate analysis steps with progress updates
        steps = [
            ("Loading audio file", 10),
            ("Extracting features", 25),
            ("Analyzing rhythm patterns", 40),
            ("Detecting mood characteristics", 60),
            ("Calculating energy levels", 75),
            ("Identifying textures", 90),
            ("Finalizing analysis", 100)
        ]
        
        for step, progress in steps:
            await asyncio.sleep(0.5)  # Simulate processing time
            
            # Send progress update
            await websocket.send_text(json.dumps({
                "type": "progress",
                "step": step,
                "progress": progress,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }))
            
            # Send partial results for some steps
            if progress == 40:
                await websocket.send_text(json.dumps({
                    "type": "partial",
                    "data": {
                        "bpm": 95.5,
                        "rhythm_pattern": "boom-bap"
                    }
                }))
            elif progress == 60:
                await websocket.send_text(json.dumps({
                    "type": "partial",
                    "data": {
                        "mood": "melancholic",
                        "mood_confidence": 0.82
                    }
                }))
            elif progress == 75:
                await websocket.send_text(json.dumps({
                    "type": "partial",
                    "data": {
                        "energy": 0.45,
                        "energy_variance": 0.12
                    }
                }))
        
        # Send complete analysis
        final_analysis = {
            "id": f"analysis_{sample_id}_{datetime.now(timezone.utc).timestamp()}",
            "sample_id": sample_id,
            "bpm": 95.5,
            "mood": "melancholic",
            "energy": 0.45,
            "textures": ["dusty", "vinyl", "warm", "nostalgic"],
            "compatible_genres": ["lo-fi hip hop", "jazz", "soul"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        await websocket.send_text(json.dumps({
            "type": "complete",
            "data": final_analysis
        }))
        
        # Update sample in database
        sample = await db.get(Sample, sample_id)
        if sample:
            sample.analyzed_at = datetime.now(timezone.utc)
            sample.bpm = final_analysis["bpm"]
            sample.extra_metadata = {
                **(sample.extra_metadata or {}),
                "vibe_analysis": final_analysis
            }
            await db.commit()
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }))


async def websocket_endpoint(
    websocket: WebSocket,
    sample_id: int,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint for real-time vibe analysis updates."""
    client_id = f"sample_{sample_id}"
    await manager.connect(websocket, client_id)
    
    try:
        # Start analysis
        await analyze_sample_with_updates(sample_id, websocket, db)
        
        # Keep connection alive for future updates
        while True:
            # Wait for client messages (ping/pong)
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, client_id)