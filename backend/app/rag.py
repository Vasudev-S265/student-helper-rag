import os
from google import genai
from dotenv import load_dotenv
from pathlib import Path
from app.vector_store import get_collection

load_dotenv(Path(__file__).resolve().parents[2]/".env")

client=genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL=os.environ["GEMINI_MODEL"]

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
    "I couldn't find that in the course material." or "That is not related to the course now, is it?" Do not use outside knowledge.
    After your answer, cite the sources you used.

    CONTEXT:
    {context}

    QUESTION: {question}"""


def answer(question:str)->dict:
    chunks=retrieve(question)
    prompt=build_prompt(question, chunks)
    response=client.models.generate_content(model=MODEL, contents=prompt)
    return {"answer":response.text, "sources":chunks}

if __name__=="__main__":
    result=answer("Who won the 2010 FIFA World cup?")
    print(result['answer'])
    print("\n---Sources---")
    for s in result["sources"]:
        print(f"{s['source']} (page {s['page']}")
