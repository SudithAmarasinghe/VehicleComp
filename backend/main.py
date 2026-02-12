"""
FastAPI backend server for vehicle market price agent.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import asyncio

from config import config
from agent import run_agent
from rag import vehicle_indexer


# Initialize FastAPI app
app = FastAPI(
    title="Vehicle Market Price Agent API",
    description="AI agent for Sri Lankan vehicle market prices",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class QueryRequest(BaseModel):
    query: str
    conversation_history: Optional[List[Dict]] = []


class QueryResponse(BaseModel):
    response: str
    vehicles: List[Dict]
    comparison: Dict
    intent: str


class HealthResponse(BaseModel):
    status: str
    message: str


# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.conversation_histories: Dict[str, List[Dict]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        if client_id not in self.conversation_histories:
            self.conversation_histories[client_id] = []
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)
    
    def get_history(self, client_id: str) -> List[Dict]:
        return self.conversation_histories.get(client_id, [])
    
    def add_to_history(self, client_id: str, message: Dict):
        if client_id not in self.conversation_histories:
            self.conversation_histories[client_id] = []
        self.conversation_histories[client_id].append(message)


manager = ConnectionManager()


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    print("Starting Vehicle Market Price Agent API...")
    
    # Seed knowledge base if empty
    try:
        from rag import get_vector_store
        vector_store = get_vector_store()
        count = vector_store.get_collection_count()
        
        if count == 0:
            print("Seeding knowledge base...")
            vehicle_indexer.seed_knowledge_base()
            print(f"Knowledge base seeded with initial data")
        else:
            print(f"Knowledge base already contains {count} documents")
    except Exception as e:
        print(f"Warning: Could not initialize knowledge base: {str(e)}")
    
    print("API ready!")


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="Vehicle Market Price Agent API is running"
    )


# REST endpoint for queries
@app.post("/api/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """
    Query the agent with a question.
    
    Args:
        request: Query request with user question and conversation history
        
    Returns:
        Agent response with vehicle data
    """
    try:
        result = run_agent(request.query, request.conversation_history)
        
        return QueryResponse(
            response=result['response'],
            vehicles=result['vehicles'],
            comparison=result['comparison'],
            intent=result['intent']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint for real-time chat
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time chat.
    
    Args:
        websocket: WebSocket connection
        client_id: Unique client identifier
    """
    await manager.connect(websocket, client_id)
    
    try:
        # Send welcome message
        await manager.send_message({
            "type": "system",
            "message": "Connected to Vehicle Market Price Agent. Ask me about vehicle prices in Sri Lanka!"
        }, websocket)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_query = message_data.get('message', '')
            
            if not user_query:
                continue
            
            # Send typing indicator
            await manager.send_message({
                "type": "typing",
                "message": "Agent is thinking..."
            }, websocket)
            
            # Get conversation history
            history = manager.get_history(client_id)
            
            # Run agent
            try:
                result = run_agent(user_query, history)
                
                # Update conversation history
                manager.add_to_history(client_id, {
                    'role': 'user',
                    'content': user_query
                })
                manager.add_to_history(client_id, {
                    'role': 'assistant',
                    'content': result['response']
                })
                
                # Send response
                await manager.send_message({
                    "type": "response",
                    "message": result['response'],
                    "vehicles": result['vehicles'],
                    "comparison": result['comparison'],
                    "intent": result['intent']
                }, websocket)
            
            except Exception as e:
                await manager.send_message({
                    "type": "error",
                    "message": f"Error processing query: {str(e)}"
                }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Client {client_id} disconnected")
    
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)


# Run the server
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=config.BACKEND_HOST,
        port=config.BACKEND_PORT,
        reload=True
    )
