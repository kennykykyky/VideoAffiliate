import json
from typing import Dict, Any
from loguru import logger

class PromptGenerator:
    def __init__(self, llm_client):
        self.llm = llm_client
    
    def analyze_sentence(self, sentence: str) -> Dict[str, Any]:
        """Analyze sentence and extract key visual elements"""
        prompt = (
            "Analyze this sentence and extract key visual elements for image generation. "
            "Focus only on concrete visual elements. Return a JSON object with these fields:\n"
            '{"main_subject": "the main visible object", '
            '"action": "what the subject is doing", '
            '"environment": "background setting", '
            '"mood": "scene atmosphere", '
            '"key_elements": ["up to 3 other important visual elements"]}\n\n'
            f"Sentence: {sentence}\n"
            "Response must be valid JSON only."
        )
        
        try:
            result = self.llm.generate(prompt)
            logger.debug(f"LLM response: {result}")  # Add debug logging
            
            # Clean up the response by removing markdown code blocks if present
            if "```" in result:
                # Extract content between code blocks
                result = result.split("```")[1]
                # Remove language identifier if present (e.g., 'json')
                if result.startswith("json"):
                    result = result[4:]
                result = result.strip()
            
            return json.loads(result)
        except Exception as e:
            logger.error(f"Error analyzing sentence: {str(e)}")
            # Return a basic fallback result
            return {
                "main_subject": sentence,
                "action": "exists",
                "environment": "natural setting",
                "mood": "neutral",
                "key_elements": []
            }
    
    def generate_midjourney_prompt(self, analysis: Dict[str, Any]) -> str:
        """Generate Midjourney prompt from analysis result"""
        # Base style settings
        style_settings = [
            "cinematic lighting",
            "8k",
            "highly detailed",
            "professional photography",
            "realistic"
        ]
        
        # Build main description
        main_description = f"{analysis['main_subject']} {analysis['action']}"
        
        # Add environment description
        if analysis['environment']:
            main_description += f", {analysis['environment']}"
        
        # Add mood/atmosphere
        if analysis['mood']:
            style_settings.insert(0, analysis['mood'])
        
        # Add key elements
        if analysis['key_elements']:
            main_description += f", with {', '.join(analysis['key_elements'])}"
        
        # Combine final prompt
        prompt = f"{main_description} --style {', '.join(style_settings)}"
        
        return prompt 