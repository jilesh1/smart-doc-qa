import os
import json
from groq import Groq
from retriever import retrieve_chunks

MODEL = "llama-3.3-70b-versatile"  # Free & fast on Groq


def _client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY missing in .env")
    return Groq(api_key=api_key)


def answer_with_claude(question: str, chunks):
    """Answer a question using retrieved document chunks."""
    context = "\n\n".join(
        [f"[Citation: {c['citation']}]\n{c['text']}" for c in chunks]
    )

    prompt = f"""You are a document Q&A assistant.
Answer ONLY using the context below.
If the answer is not present in the context, say: "I could not find this information in the uploaded document."
Every factual claim must include a citation using this exact format: [source - chunk number].
Do not use outside knowledge.

CONTEXT:
{context}

QUESTION:
{question}
"""

    response = _client().chat.completions.create(
        model=MODEL,
        max_tokens=1200,
        temperature=0.1,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def generate_welcome_json(doc_id: str):
    """Generate a welcome summary and suggested questions for a document."""
    chunks = retrieve_chunks(doc_id, "summary main topics important questions", top_k=5)
    context = "\n\n".join([c["text"] for c in chunks])

    prompt = f"""Using ONLY this document context, return valid JSON only.
No markdown, no explanation, no code fences.
JSON schema:
{{
  "summary": "short friendly summary of the document",
  "questions": ["question 1", "question 2", "question 3", "question 4"]
}}

Context:
{context}
"""

    response = _client().chat.completions.create(
        model=MODEL,
        max_tokens=700,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.choices[0].message.content.strip()

    # Strip markdown code fences if model adds them
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "summary": "I uploaded and indexed your document successfully.",
            "questions": [
                "What is this document about?",
                "What are the key points?",
                "Can you summarize the important sections?",
                "What should I know first?",
            ],
        }