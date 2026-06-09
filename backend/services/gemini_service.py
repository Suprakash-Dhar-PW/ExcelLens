import os
from google import genai
from google.genai import types

class GeminiService:
    def __init__(self):
        # Assumes GEMINI_API_KEY is in the environment
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            import logging
            logging.warning("GEMINI_API_KEY not found in environment")
            
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None
        
    def generate_chat_response(self, messages: list[dict], system_instruction: str = None) -> str:
        """
        messages: [{"role": "user"|"model", "parts": [{"text": "Hello"}]}]
        """
        if not self.client:
            return "I am offline. Please set the GEMINI_API_KEY in the backend/.env file."
            
        try:
            # Transform history into the required format if needed
            formatted_contents = []
            for msg in messages:
                role = "user" if msg["sender"] == "user" else "model"
                formatted_contents.append({
                    "role": role,
                    "parts": [{"text": msg["message"]}]
                })
            
            config = types.GenerateContentConfig()
            if system_instruction:
                config.system_instruction = system_instruction
                
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=formatted_contents,
                config=config
            )
            return response.text
        except Exception as e:
            import logging
            logging.error(f"Gemini generation error: {e}")
            return "Sorry, I encountered an error while processing your request."
