from pathlib import Path
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

DOCS_DIR=Path(__file__).resolve().parents[2]/"data"/"docs"

def load_pdfs(docs_dir:Path=DOCS_DIR)-> list[dict]:
    pages=[]
    for pdf_path in sorted(docs_dir.glob("*.pdf")):
        reader=PdfReader(pdf_path)
        for page_num, page in enumerate(reader.pages, start=1):
            text=page.extract_text() or ""
            if text.strip():
                pages.append({
                    "text":text,
                    "source":pdf_path.name,
                    "page":page_num
                })
    return pages




def chunk_pages(pages: list[dict], chunk_size: int = 800, chunk_overlap:int = 150) -> list[dict]:
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks=[]
    for p in pages:
        for i, piece in enumerate(splitter.split_text(p["text"])):
            chunks.append({
                "text":piece,
                "source":p["source"],
                "page":p["page"],
                "chunk_id": f"{p['source']}-p{p['page']}-c{i}",
            })
    return chunks

if __name__=="__main__":
    pages=load_pdfs()
    chunks=chunk_pages(pages)
    print(f"Loaded {len(pages)} pages. -> {len(chunks)} chunks.")
    print("\n Sample chunk ")
    print(chunks[0]["chunk_id"])
    print(chunks[0]["text"])
