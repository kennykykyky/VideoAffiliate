from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import requests
import json
import base64
from loguru import logger
from app.config import config
from openai import OpenAI
from app.models.schema import VideoAspect

class ImageGenerationProvider(ABC):
    @abstractmethod
    def generate_image(self, prompt: str, aspect: VideoAspect = VideoAspect.portrait) -> str:
        """Generate image from prompt and return the URL or base64 data"""
        pass

class StableDiffusionProvider(ImageGenerationProvider):
    def __init__(self):
        self.api_key = config.app.get("stable_diffusion_api_key", "")
        self.api_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        if not self.api_key:
            raise ValueError("Stable Diffusion API key not configured")
    
    def generate_image(self, prompt: str, aspect: VideoAspect = VideoAspect.portrait) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 50,
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if "artifacts" in result and len(result["artifacts"]) > 0:
                return result["artifacts"][0]["base64"]
            else:
                raise ValueError("No image generated in response")
                
        except Exception as e:
            logger.error(f"Stable Diffusion API call failed: {str(e)}")
            raise

class DallEProvider(ImageGenerationProvider):
    def __init__(self):
        self.api_key = config.app.get("dalle_api_key", "")
        self.model = config.app.get("dalle_model", "dall-e-3")
        self.base_url = config.app.get("openai_base_url", "https://api.openai.com/v1")
        
        if not self.api_key:
            raise ValueError("DALL-E API key not configured")
        
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
    
    def generate_image(self, prompt: str, aspect: VideoAspect = VideoAspect.portrait) -> str:
        try:
            response = self.client.images.generate(
                model=self.model,
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
                response_format="b64_json"
            )
            
            if response.data and len(response.data) > 0:
                return response.data[0].b64_json
            else:
                raise ValueError("No image generated in response")
                
        except Exception as e:
            logger.error(f"DALL-E API call failed: {str(e)}")
            raise

class MidjourneyProvider(ImageGenerationProvider):
    def __init__(self):
        self.api_key = config.app.get("midjourney_api_key", "")
        self.api_url = config.app.get("midjourney_api_url", "https://api.midjourney.com/v1/imagine")
        
        if not self.api_key:
            raise ValueError("Midjourney API key not configured")
    
    def generate_image(self, prompt: str, aspect: VideoAspect = VideoAspect.portrait) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "width": 1024,
            "height": 1024,
            "quality": "standard",
            "style": "raw"
        }
        
        try:
            # Start the generation
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if "taskId" not in result:
                raise ValueError("No task ID in response")
            
            task_id = result["taskId"]
            
            # Poll for results
            status_url = f"{self.api_url}/status/{task_id}"
            max_attempts = 30
            attempts = 0
            
            while attempts < max_attempts:
                status_response = requests.get(status_url, headers=headers)
                status_response.raise_for_status()
                status = status_response.json()
                
                if status["status"] == "completed":
                    # Convert URL to base64
                    image_response = requests.get(status["imageUrl"])
                    image_response.raise_for_status()
                    return base64.b64encode(image_response.content).decode()
                elif status["status"] == "failed":
                    raise ValueError(f"Image generation failed: {status.get('error', 'Unknown error')}")
                
                attempts += 1
                import time
                time.sleep(10)  # Wait 10 seconds between checks
            
            raise TimeoutError("Image generation timed out")
                
        except Exception as e:
            logger.error(f"Midjourney API call failed: {str(e)}")
            raise

class ImageGenerationClient:
    def __init__(self):
        self.provider = self._init_provider()
    
    def _init_provider(self) -> ImageGenerationProvider:
        """Initialize the configured image generation provider"""
        provider_name = config.app.get("image_provider", "stable-diffusion")
        
        if provider_name == "stable-diffusion":
            return StableDiffusionProvider()
        elif provider_name == "dalle":
            return DallEProvider()
        elif provider_name == "midjourney":
            return MidjourneyProvider()
        else:
            raise ValueError(f"Unsupported image provider: {provider_name}")
    
    def generate_image(self, prompt: str, aspect: VideoAspect = VideoAspect.portrait) -> str:
        """Generate image using the configured provider"""
        try:
            return self.provider.generate_image(prompt, aspect)
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            raise 