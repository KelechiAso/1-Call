# filename: main.py
# This is the main FastAPI application file for a streaming LLM backend.

import os
import traceback
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, AsyncGenerator

# --- Service Import ---
from .api.openai_service import stream_llm_response

# --- App Setup ---
app = FastAPI(
    title="Streaming Chatbot Microservice",
    description="Provides streaming responses using an OpenAI LLM with history."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Models ---
class ChatRequest(BaseModel):
    user_id: str = "default_user"
    query: str
    history: List[Dict[str, str]] = []

# --- Routes ---
@app.get("/", response_class=FileResponse, include_in_schema=False)
async def read_index():
    html_file_path = "app/static/htmlsim.html"
    if not os.path.exists(html_file_path):
        raise HTTPException(status_code=404, detail="Index HTML not found.")
    return FileResponse(html_file_path)

@app.post("/chat-stream")
async def handle_chat_stream(request: ChatRequest):
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
        
    print(f"--- /chat-stream CALLED by user: {request.user_id}, query: '{request.query[:60]}...' ---")
    
    try:
        return StreamingResponse(
            stream_llm_response(request.query, request.history),
            media_type="text/event-stream"
        )
    except Exception as e:
        error_type = type(e).__name__
        print(f"!!! UNHANDLED EXCEPTION in /chat-stream endpoint: {error_type} - {e}")
        traceback.print_exc()
        return StreamingResponse(
            iter([f"data: {json.dumps({'error': True, 'message': f'Server error: {error_type}'})}\n\n"]),
            media_type="text/event-stream"
        )

print("--- app/main.py: Application startup complete. ---")
