from app.services.gemini_service import ask_gemini

def summarize_document(document_text: str) -> str:
    prompt = f'''
Summarize the following academic document.

Return:
1. Main topic
2. Objective
3. Methodology
4. Key findings
5. Conclusion

Document:
{document_text[:15000]}
'''
    return ask_gemini(prompt)
