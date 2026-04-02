def chunk_text(text: str, chunk_size: int = 1800, overlap: int = 200) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += max(1, chunk_size - overlap)
    return chunks
