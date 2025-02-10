import os
from loguru import logger
from app.services.llm import get_llm_client
from app.services.midjourney.prompt import PromptGenerator
from app.services.midjourney.client import ImageGenerationClient
import base64

def save_base64_image(base64_str: str, filename: str):
    """Save base64 string as image file"""
    try:
        image_data = base64.b64decode(base64_str)
        with open(filename, 'wb') as f:
            f.write(image_data)
        logger.info(f"Saved image to {filename}")
    except Exception as e:
        logger.error(f"Error saving image: {str(e)}")

def test_image_generation():
    """Test the complete flow: text analysis -> prompt generation -> image generation"""
    # Test sentence
    test_sentence = "A cat playing with yarn in a sunny living room"
    
    try:
        # Initialize components
        llm_client = get_llm_client()
        prompt_generator = PromptGenerator(llm_client)
        image_client = ImageGenerationClient()
        
        # Generate prompt
        print("\nAnalyzing sentence and generating prompt...")
        analysis = prompt_generator.analyze_sentence(test_sentence)
        prompt = prompt_generator.generate_midjourney_prompt(analysis)
        
        print(f"\nGenerated prompt: {prompt}")
        
        # Generate image
        print("\nGenerating image...")
        image_data = image_client.generate_image(prompt)
        
        # Save the image
        os.makedirs("tests/generated_images", exist_ok=True)
        filename = "tests/generated_images/test_image.png"
        save_base64_image(image_data, filename)
        
        print(f"\nImage generated and saved to: {filename}")
        
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    print("\n=== Image Generation Test ===")
    test_image_generation() 