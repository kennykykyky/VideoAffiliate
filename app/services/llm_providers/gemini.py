import google.generativeai as genai
from loguru import logger
from app.config import config

class GeminiProvider:
    def __init__(self):
        self.api_key = config.app.get("gemini_api_key", "")
        self.model_name = config.app.get("gemini_model_name", "gemini-1.0-pro")
        
        if not self.api_key:
            raise ValueError("Gemini API key is not configured")
            
        # Configure the Gemini client
        genai.configure(api_key=self.api_key, transport="rest")
        
        # Set up generation config
        self.generation_config = {
            "temperature": 0.5,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        
        # Set up safety settings
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
        ]
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config,
            safety_settings=self.safety_settings,
        )
    
    def generate(self, prompt: str) -> str:
        """Generate text using Gemini API"""
        try:
            response = self.model.generate_content(prompt)
            if not response.candidates:
                raise ValueError("No response generated")
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {str(e)}")
            raise 