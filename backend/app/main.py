from fastapi import FastAPI
from pydantic import BaseModel, Field
from app.rag import answer
from app.db import init_db, log_interaction

app = FastAPI(title="Student Helper RAG")
init_db()

class Askrequest(BaseModel):
    question: str =Field(min_length=1, max_length=500)
    session_id:str |None= Field(default=None, max_length=64)

    
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