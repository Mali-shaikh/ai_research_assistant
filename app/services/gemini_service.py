import google.generativeai as genai
from app.core.config import settings
from google.api_core.exceptions import GoogleAPIError

genai.configure(api_key=settings.GEMINI_API_KEY)

def ask_gemini(prompt: str, system: str = "You are an academic research assistant.") -> str:
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "sk-placeholder-replace-me":
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    try:
        model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            system_instruction=system
        )
        
        response = model.generate_content(prompt)
        if response.text:
            return response.text.strip()
        return "No response generated."
    except GoogleAPIError as e:
        return f"Gemini API Error: {e.message}"
    except ValueError as e:
        return f"Response blocked or invalid: {str(e)}"
    except Exception as e:
        return f"An error occurred while calling Gemini: {str(e)}"
