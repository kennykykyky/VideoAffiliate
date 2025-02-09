import json
import requests
from loguru import logger
from app.config import config

class DeepseekProvider:
    def __init__(self):
        self.api_key = config.app.get("deepseek_api_key", "")
        self.base_url = config.app.get("deepseek_base_url", "https://api.deepseek.com")
        self.model = config.app.get("deepseek_model_name", "deepseek-chat")
        
        if not self.api_key:
            raise ValueError("Deepseek API key is not configured")
    
    def generate(self, prompt: str) -> str:
        """调用 Deepseek API 生成文本"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"Deepseek API 调用失败: {str(e)}")
            if response := getattr(e, "response", None):
                logger.error(f"Response: {response.text}")
            raise 