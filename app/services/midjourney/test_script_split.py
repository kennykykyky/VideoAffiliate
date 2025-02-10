from loguru import logger
from app.services.llm import get_llm_client
from app.services.midjourney.prompt import PromptGenerator

def test_script_splitting():
    """Test the script splitting and prompt generation for multiple sentences"""
    # Test script with multiple lines
    test_script = """A cat playing with yarn in a sunny living room.
A dog chasing a ball in the park.
Children laughing on a playground.
Sunset over a peaceful beach."""

    try:
        # Initialize components
        llm_client = get_llm_client()
        generator = PromptGenerator(llm_client)
        
        # Test script splitting
        print("\nTesting script splitting...")
        sentences = generator.split_script(test_script)
        print(f"\nSplit into {len(sentences)} sentences:")
        for i, sentence in enumerate(sentences, 1):
            print(f"{i}. {sentence}")
        
        # Test prompt generation for all sentences
        print("\nGenerating prompts for each sentence...")
        results = generator.generate_prompts_for_script(test_script)
        
        # Display results
        print("\nGenerated prompts for each sentence:")
        for i, result in enumerate(results, 1):
            print(f"\n=== Sentence {i} ===")
            print(f"Original: {result['sentence']}")
            print(f"Analysis: {result['analysis']}")
            print(f"Prompt: {result['prompt']}")
            
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    print("\n=== Script Splitting and Prompt Generation Test ===")
    test_script_splitting() 