from fastapi import FastAPI

app = FastAPI(title="Student Helper RAG")

@app.get("/health")
def health():
    return {"status": "ok"}