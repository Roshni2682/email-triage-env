
"""
FastAPI server exposing the EmailTriageEnv via HTTP.
This is the entry point for Hugging Face Spaces deployment.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union, Optional
import uuid

from environment import EmailTriageEnv
from models import Action1, Action2, Action3

app = FastAPI(
    title="Email Triage OpenEnv",
    description="A real-world email triage environment for AI agent training.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store
sessions: dict[str, EmailTriageEnv] = {}


class CreateSessionRequest(BaseModel):
    task_id: str = "task1"
    seed: int = 42


class StepRequest(BaseModel):
    session_id: str
    action: dict  # Raw dict, will be parsed based on task


@app.get("/")
def root():
    return {
        "name": "Email Triage OpenEnv",
        "version": "1.0.0",
        "tasks": ["task1", "task2", "task3"],
        "endpoints": ["/reset", "/step", "/state", "/info"]
    }


@app.post("/reset")
def reset(req: CreateSessionRequest = None):
    session_id = str(uuid.uuid4())
    try:
        if req is None:
            req = CreateSessionRequest()
        env = EmailTriageEnv(task_id=req.task_id, seed=req.seed)
        obs = env.reset()
        sessions[session_id] = env
        return {"session_id": session_id, "observation": obs.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/step")
def step(req: StepRequest):
    env = sessions.get(req.session_id)
    if not env:
        raise HTTPException(status_code=404, detail="Session not found. Call /reset first.")

    task_id = env.task_id
    try:
        if task_id == "task1":
            action = Action1(**req.action)
        elif task_id == "task2":
            action = Action2(**req.action)
        else:
            action = Action3(**req.action)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid action: {str(e)}")

    try:
        result = env.step(action)
        return result.model_dump()
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/state/{session_id}")
def state(session_id: str):
    env = sessions.get(session_id)
    if not env:
        raise HTTPException(status_code=404, detail="Session not found.")
    return env.state().model_dump()


@app.get("/info/{task_id}")
def info(task_id: str):
    try:
        env = EmailTriageEnv(task_id=task_id)
        return env.get_task_info()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}