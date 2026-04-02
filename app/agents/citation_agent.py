from app.services.gemini_service import ask_gemini

def extract_citations(document_text: str) -> str:
    prompt = f'''
Extract likely references, authors, and publication years from the text below.
Return the result as a clean bullet list.

Text:
{document_text[:15000]}
'''
    return ask_gemini(prompt)
