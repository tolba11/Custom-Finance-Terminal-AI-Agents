"""Turn uploaded files of any type into model-ready content.

Returns Claude-native blocks (vision for images, document for PDFs) plus
extracted text for text-only providers like Perplexity."""
import base64
import io
import re
import zipfile

MAX_TEXT_PER_FILE = 30000
MAX_TEXT_TOTAL = 80000

IMAGE_TYPES = {"png": "image/png", "jpg": "image/jpeg",
               "jpeg": "image/jpeg", "gif": "image/gif",
               "webp": "image/webp"}


def _ext(name: str) -> str:
    return name.rsplit(".", 1)[-1].lower() if "." in name else ""


def _pdf_text(data: bytes) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        return "\n".join((p.extract_text() or "") for p in reader.pages[:40])
    except Exception:
        return ""


def _docx_text(data: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            xml = z.read("word/document.xml").decode("utf-8", "ignore")
        text = re.sub(r"</w:p>", "\n", xml)
        return re.sub(r"<[^>]+>", "", text)
    except Exception:
        return ""


def _sheet_text(data: bytes, ext: str) -> str:
    try:
        import pandas as pd
        df = (pd.read_excel(io.BytesIO(data), nrows=300) if ext != "csv"
              else pd.read_csv(io.BytesIO(data), nrows=300))
        return df.to_csv(index=False)
    except Exception:
        return ""


def process_files(files):
    """files: streamlit UploadedFile list.
    Returns (claude_blocks, text_context, chips, notes)."""
    blocks, texts, chips, notes = [], [], [], []
    total = 0
    for f in files or []:
        name = getattr(f, "name", "file")
        data = f.getvalue()
        ext = _ext(name)
        chips.append(name)
        if ext in IMAGE_TYPES:
            blocks.append({"type": "image", "source": {
                "type": "base64", "media_type": IMAGE_TYPES[ext],
                "data": base64.b64encode(data).decode()}})
            notes.append(f"{name}: image — viewable by Claude models only")
            continue
        if ext == "pdf":
            blocks.append({"type": "document", "source": {
                "type": "base64", "media_type": "application/pdf",
                "data": base64.b64encode(data).decode()}})
            extracted = _pdf_text(data)
        elif ext == "docx":
            extracted = _docx_text(data)
        elif ext in ("xlsx", "xls", "csv"):
            extracted = _sheet_text(data, ext)
        else:
            try:
                extracted = data.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    extracted = data.decode("latin-1")
                except Exception:
                    extracted = ""
        if extracted:
            snippet = extracted[:MAX_TEXT_PER_FILE]
            if total + len(snippet) > MAX_TEXT_TOTAL:
                snippet = snippet[:max(0, MAX_TEXT_TOTAL - total)]
            total += len(snippet)
            if snippet:
                texts.append(f"===== FILE: {name} =====\n{snippet}")
        elif ext != "pdf" and ext not in IMAGE_TYPES:
            notes.append(f"{name}: could not extract text from this "
                         f"file type; only the filename is visible")
    return blocks, "\n\n".join(texts), chips, notes
