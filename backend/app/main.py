from fastapi import FastAPI, HTTPException
from typing import Literal
from pydantic import BaseModel, Field
from app.rag import answer
from app.db import init_db, log_interaction, log_feedback

app = FastAPI(title="Student Helper RAG")
init_db()

class Askrequest(BaseModel):
    question: str =Field(min_length=1, max_length=500)
    session_id:str |None= Field(default=None, max_length=64)

class FeedbackRequest(BaseModel):
    interaction_id:int
    rating:Literal[1, -1]
    comment:str | None = Field(default=None, max_length=1000)

    
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(req: Askrequest):
    result=answer(req.question)
    interaction_id=log_interaction(
        req.session_id, req.question, result["answer"], result["sources"]

    )
    return {**result, "interaction_id":interaction_id}

@app.post("/feedback")
def feeback(req:FeedbackRequest):
    ok=log_feedback(req.interaction_id, req.rating, req.comment)
    if not ok:
        raise HTTPException(status_code=404, detail="Unknown interaction_id")

    return {"status":"saved"}

