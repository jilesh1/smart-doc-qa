import os
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from parser import extract_text_from_pdf
from chunker import split_text
from embedder import add_chunks_to_chroma
from retriever import retrieve_chunks, list_documents
from llm import answer_with_claude, generate_welcome_json

load_dotenv()

app = FastAPI(title="Smart Document Q&A API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def clean_doc_id(filename: str) -> str:
    """Sanitize filename for ChromaDB collection/doc id usage."""
    base = os.path.basename(filename).replace(" ", "_")
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
    cleaned = "".join(ch for ch in base if ch in allowed)
    cleaned = cleaned.strip("._-")
    if not cleaned:
        cleaned = "document"
    return cleaned[:120]


class AskRequest(BaseModel):
    doc_id: str
    question: str


class WelcomeRequest(BaseModel):
    doc_id: str


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    doc_id = clean_doc_id(file.filename)
    file_path = os.path.join(UPLOAD_DIR, doc_id)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text_from_pdf(file_path)
    if not text.strip():
        raise HTTPException(status_code=400, detail="No text found in PDF")

    chunks = split_text(text)
    add_chunks_to_chroma(doc_id=doc_id, chunks=chunks, source_name=file.filename)

    welcome = generate_welcome_json(doc_id)

    return {
        "message": "PDF uploaded and indexed successfully",
        "doc_id": doc_id,
        "filename": file.filename,
        "chunks": len(chunks),
        "welcome": welcome,
    }


@app.post("/ask")
async def ask_question(req: AskRequest):
    results = retrieve_chunks(req.doc_id, req.question, top_k=5)
    if not results:
        raise HTTPException(status_code=404, detail="No chunks found for this document")

    answer = answer_with_claude(req.question, results)
    return {"answer": answer, "sources": results}


@app.post("/welcome")
async def welcome(req: WelcomeRequest):
    return generate_welcome_json(req.doc_id)


@app.get("/documents")
async def documents():
    return {"documents": list_documents()}
