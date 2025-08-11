"""
filename: main.py FastAPI application file for a the LLM backend.

"""

import os
import traceback
import json
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, AsyncGenerator
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from dotenv import load_dotenv 

#  Service Import 
from .api.openai_service import stream_llm_response

#  App Setup 
app = FastAPI(
    title="GameNerd",
    description="Provides gaming-related responses using an OpenAI LLM with history."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#--- new commit adding authentication

load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

if not SECRET_KEY:
    raise ValueError("CRITICAL: JWT_SECRET_KEY is not set in environment variables.")

# at this stage: checking for a bearer token in the header
oauth2_scheme = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    """
    Dependency used to validate the JWT token and return the user Info.
    more like the bouncer for the API.
    If the token is invalid or expired, it would raises an HTTPException.
    else, it returns the user ID and other info extracted from the token.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")  # 'sub' is a standard JWT field for subject/user_id
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# defining the API Models -
class ChatRequest(BaseModel):
    #==> user_id: str = "default_user" <==#
    query: str
    history: List[Dict[str, str]] = []

# creating the Routes --
@app.get("/", response_class=FileResponse, include_in_schema=False)
async def read_index():
    html_file_path = "app/static/htmlsim.html"  #==> Define the file path for the frontend HTML file <==# may change during deployment
    if not os.path.exists(html_file_path):
        raise HTTPException(status_code=404, detail="Index HTML not found.")
    return FileResponse(html_file_path)

@app.post("/chat-stream")
async def handle_chat_stream(
    request: ChatRequest,
    #==> Here we use the depend and the funct defined earlier to control authentication <==#
    current_user_id: str = Depends(get_current_user_id)
):
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
