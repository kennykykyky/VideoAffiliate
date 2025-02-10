from enum import Enum
from dataclasses import dataclass
from typing import Optional

class MaterialType(Enum):
    VIDEO = "video"
    IMAGE = "image"
    MIDJOURNEY = "midjourney"

@dataclass
class MaterialInfo:
    type: MaterialType = MaterialType.VIDEO
    provider: str = ""
    url: str = ""
    duration: float = 0.0
    prompt: str = ""  # For AI-generated images
    sentence: str = ""  # Original sentence that generated this material
    
    def __init__(
        self,
        type: MaterialType = MaterialType.VIDEO,
        provider: str = "",
        url: str = "",
        duration: float = 0.0,
        prompt: str = "",
        sentence: str = ""
    ):
        self.type = type
        self.provider = provider
        self.url = url
        self.duration = duration
        self.prompt = prompt
        self.sentence = sentence 