import fitz  # PyMuPDF


def extract_text_from_pdf(file_path: str) -> str:
    text = []
    with fitz.open(file_path) as doc:
        for page_num, page in enumerate(doc, start=1):
            page_text = page.get_text("text")
            if page_text.strip():
                text.append(f"\n[Page {page_num}]\n{page_text}")
    return "\n".join(text)
