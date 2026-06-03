from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ollama_service import get_ollama_response
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str

@app.post("/chat")
async def chat(req: ChatRequest):
    history = sessions.get(req.session_id, [])
    response = await get_ollama_response(req.message, history)
    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": response})
    sessions[req.session_id] = history[-20:]
    return {"response": response}

@app.get("/")
async def root():
    return {"status": "ok"}