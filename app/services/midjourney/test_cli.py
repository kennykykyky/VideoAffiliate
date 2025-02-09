import json
import os
from datetime import datetime
from typing import Dict, Any

from loguru import logger
from app.services.midjourney.prompt import PromptGenerator
from app.services.llm import get_llm_client

def save_test_result(sentence: str, analysis: Dict[str, Any], prompt: str):
    """Save test result to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result = {
        "sentence": sentence,
        "analysis": analysis,
        "prompt": prompt,
        "timestamp": timestamp
    }
    
    # Create test results directory
    os.makedirs("tests/results", exist_ok=True)
    
    # Save result
    filename = f"tests/results/test_result_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\nResult saved to: {filename}")

def test_single_prompt():
    """Test prompt generation for a single sentence"""
    try:
        # Initialize LLM client and prompt generator
        llm_client = get_llm_client()
        generator = PromptGenerator(llm_client)
        
        # Get user input
        sentence = input("\nEnter a test sentence: ")
        
        # Generate analysis and prompt
        print("\nAnalyzing sentence...")
        analysis = generator.analyze_sentence(sentence)
        prompt = generator.generate_midjourney_prompt(analysis)
        
        # Display results
        print("\nAnalysis result:")
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
        print("\nGenerated Midjourney prompt:")
        print(prompt)
        
        # Ask to save result
        if input("\nSave this result? (y/n): ").lower() == 'y':
            save_test_result(sentence, analysis, prompt)
    
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        print(f"\nError: {str(e)}")

def test_batch_sentences():
    """Test prompt generation for a batch of preset sentences"""
    test_sentences = [
        "Sunlight filtering through leaves, shining on a cat",
        "Business people working focused in the office",
        "Children running happily on the playground",
        "Rainbow stretching across the sky after rain",
        "Elderly people playing chess in the park"
    ]
    
    try:
        llm_client = get_llm_client()
        generator = PromptGenerator(llm_client)
        
        for i, sentence in enumerate(test_sentences, 1):
            print(f"\nTest sentence {i}/{len(test_sentences)}: {sentence}")
            print("="*50)
            
            analysis = generator.analyze_sentence(sentence)
            prompt = generator.generate_midjourney_prompt(analysis)
            
            print("\nAnalysis result:")
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
            print("\nGenerated prompt:")
            print(prompt)
            print("\n" + "="*50)
            
            # Automatically save each test result
            save_test_result(sentence, analysis, prompt)
            
    except Exception as e:
        logger.error(f"Error during batch testing: {str(e)}")
        print(f"\nError: {str(e)}")

def main():
    print("\n=== Midjourney Prompt Generation Test Tool ===")
    print("This tool tests text to Midjourney prompt conversion")
    print("="*50)
    
    while True:
        print("\nSelect operation:")
        print("1. Test single sentence")
        print("2. Test preset sentences")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            test_single_prompt()
        elif choice == "2":
            test_batch_sentences()
        elif choice == "3":
            print("\nThank you for using! Goodbye!")
            break
        else:
            print("\nInvalid choice, please try again")

if __name__ == "__main__":
    main() 