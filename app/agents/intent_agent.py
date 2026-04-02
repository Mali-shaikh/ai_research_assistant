def detect_intent(user_input: str) -> str:
    text = user_input.lower().strip()
    if any(k in text for k in ["summarize", "summary", "brief", "overview"]):
        return "summarize"
    if any(k in text for k in ["citation", "citations", "reference", "references", "authors"]):
        return "citation"
    if any(k in text for k in ["compare", "comparison", "difference between"]):
        return "compare"
    if any(k in text for k in ["explain", "what is", "how", "why", "question", "?"]):
        return "qa"
    return "general"
