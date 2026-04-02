from app.services.gemini_service import ask_gemini

def answer_question(document_text: str, question: str) -> str:
    prompt = f'''
Answer the question using only the document below.
If the answer is not in the document, say so clearly.

Document:
{document_text[:15000]}

Question:
{question}
'''
    return ask_gemini(prompt)
