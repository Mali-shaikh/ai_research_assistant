from app.services.gemini_service import ask_gemini

def compare_documents(doc1: str, doc2: str) -> str:
    prompt = f'''
Compare the following two research documents.

Return:
1. Common theme
2. Differences in methodology
3. Differences in findings
4. Strengths and weaknesses
5. Final summary

Document 1:
{doc1[:10000]}

Document 2:
{doc2[:10000]}
'''
    return ask_gemini(prompt)
