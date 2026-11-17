from fastapi import FastAPI, HTTPException, Request
from typing import Literal
from pydantic import BaseModel, Field
from app.rag import answer, LLMBusyError
from app.db import init_db, log_interaction, log_feedback
from fastapi.middleware.cors import CORSMiddleware
from app.rate_limit import SlidingWindowLimiter, DailyCap
import os

ip_limiter=SlidingWindowLimiter(int(os.environ.get("ASK_PER_IP_PER_MIN", 40)), 60)
session_limiter=SlidingWindowLimiter(int(os.environ.get("ASK_PER_SESSION_PER_MIN", 5)), 60)
feedback_limiter=SlidingWindowLimiter(30, 60)
daily_cap=DailyCap(int(os.environ.get("DAILY_ASK_CAP", 800)))

def client_ip(request:Request)->str:
    forwarded=request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"



app = FastAPI(title="Student Helper RAG")
init_db()

class Askrequest(BaseModel):
    question: str =Field(min_length=1, max_length=500)
    session_id:str |None= Field(default=None, max_length=64)

class FeedbackRequest(BaseModel):
    interaction_id:int
    helpful: bool
    comment:str | None = Field(default=None, max_length=1000)
    
origins = [
    o.strip().rstrip("/")
    for o in os.environ.get("FRONTEND_ORIGINS", "http://localhost:5173").split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
    
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(req: Askrequest, request: Request):
    ip_ok=ip_limiter.allow(client_ip(request))
    session_ok=session_limiter.allow(req.session_id) if req.session_id else True


    if not(ip_ok and session_ok):
        raise HTTPException(
            status_code=429,
            detail="You are asking too fast. Wait a few seconds and try again.",
            headers={"Retry-after":"30"},
        )

    if not daily_cap.allow():
        raise HTTPException(
            status_code=429,
            detail="The assistant has hit its daily limit. Please try again tomorrow.",
        )


    try:
        result=answer(req.question)
    except LLMBusyError:
        raise HTTPException(
            status_code=503,
            detail="I'm a bit busy right now, try again later.",

        )
    interaction_id=log_interaction(
        req.session_id, req.question, result["answer"], result["sources"], result["model"]
    )

    return{**result, "interaction_id": interaction_id}


    
@app.post("/feedback")
def feeback(req:FeedbackRequest, request:Request):
    if not feedback_limiter.allow(client_ip(request)):
        raise HTTPException(status_code= 429, detail="Too many requests. Please slow down.")

    ok=log_feedback(req.interaction_id, req.helpful, req.comment)
    if not ok:
        raise HTTPException(status_code=404, detail="Unknown interaction_id")

    return {"status":"saved"}

