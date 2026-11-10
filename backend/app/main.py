from fastapi import FastAPI
from pydantic import BaseModel, Field
from app.rag import answer

app = FastAPI(title="Student Helper RAG")


class Askrequest(BaseModel):
    question: str =Field(min_length=1, max_length=500)

    
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(req: Askrequest):
    return answer(req.question)