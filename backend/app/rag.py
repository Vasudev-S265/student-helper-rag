import os
from google import genai
from google.genai import errors
from dotenv import load_dotenv
from pathlib import Path
from app.vector_store import get_collection
import time

load_dotenv(Path(__file__).resolve().parents[2]/".env")

client=genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODELS=[m.strip() for m in os.environ["GEMINI_MODEL"].split(",")]


class LLMBusyError(Exception):
    """Raised when every model fails."""

def retrieve(question:str, k: int=4)->list[dict]:
    collection=get_collection()
    results=collection.query(query_texts=[question], n_results=k)
    return[
        {"text":doc, "source":meta["source"], "page":meta["page"]}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]


def build_prompt(question: str, chunks:list[dict])->str:
    context = "\n\n".join(
        f"[{i}] (Source: {c['source']}, page {c['page']})\n{c['text']}"
        for i, c in enumerate(chunks, start=1)
    )
    return f"""You are a helpful study assistant. Answer the student's question
    using ONLY the context below. If the context does not contain the answer, say
    "I couldn't find that in the course material." or "That is not related to the course now, is it?" or someother sassy reply, according to the question asked. Do not use outside knowledge.
    After your answer, cite the sources you used in the form (filename, page N),
    using the filenames shown in the context. Never cite by number alone.

    CONTEXT:
    {context}

    QUESTION: {question}"""

def generate_with_fallback(prompt:str)-> tuple[str, str]:
    for model in MODELS:
        for attempt in range(3):
            try:
                response=client.models.generate_content(model=model, contents=prompt)
                return response.text, model
            except errors.APIError as e:
                if e.code in (404, 429):
                    break
                if e.code in (500, 503, 504):
                    time.sleep(2**attempt)
                    continue
                raise
    raise LLMBusyError()


def answer(question:str)->dict:
    chunks=retrieve(question)
    prompt=build_prompt(question, chunks)
    text, model=generate_with_fallback(prompt)
    return{"answer":text, "sources":chunks, "model":model}

if __name__=="__main__":
    result=answer("What is narrow AI?")
    print(result['answer'])
    print("\n---Sources---")
    for s in result["sources"]:
        print(f"{s['source']} (page {s['page']}")
