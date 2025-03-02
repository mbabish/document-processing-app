import requests
import json
import argparse

def test_llm_api(prompt, max_tokens=100, temperature=0.7):
    """
    Test the LLM API by sending a request and printing the response.
    
    Args:
        prompt (str): The prompt to send to the LLM API
        max_tokens (int): Maximum number of tokens to generate
        temperature (float): Temperature for text generation (0.0-1.0)
    """
    url = "http://localhost:8000/api/generate"
    
    payload = {
        "prompt": prompt,
        "max_new_tokens": max_tokens,
        "temperature": temperature,
        "stop_sequences": ["\n\n"]
    }
    
    try:
        # Check if the API is up
        health_check = requests.get("http://localhost:8000/")
        if health_check.status_code != 200:
            print(f"API health check failed with status {health_check.status_code}")
            return
            
        model_loaded = health_check.json().get('model_loaded', False)
        if not model_loaded:
            print("Warning: Model is not yet loaded. Request may fail.")
        
        # Send the request
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n--- LLM Response ---")
            print(f"Text: {result.get('text', 'No text generated')}")
            
            usage = result.get('usage', {})
            if usage:
                print("\n--- Token Usage ---")
                print(f"Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
                print(f"Completion tokens: {usage.get('completion_tokens', 'N/A')}")
                print(f"Total tokens: {usage.get('total_tokens', 'N/A')}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
    
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the LLM API. Make sure it's running.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the LLM API")
    parser.add_argument("prompt", type=str, help="The prompt to send to the LLM API")
    parser.add_argument("--max-tokens", type=int, default=100, help="Maximum number of tokens to generate")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature for text generation (0.0-1.0)")
    
    args = parser.parse_args()
    
    test_llm_api(args.prompt, args.max_tokens, args.temperature)
