import logging
import httpx
import asyncio
import json
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("main")

# Initialize FastAPI app
app = FastAPI()

# Ollama API configuration
OLLAMA_API_BASE = os.environ.get("OLLAMA_API_BASE", "http://ollama:11434/api")
# Get default model from environment variable or use tinyllama as fallback
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "tinyllama")

# Check if Ollama server is ready
is_ollama_ready = False

# Request model
class TextRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 256  # Will be converted to max_tokens for Ollama
    temperature: float = 0.7
    stop_sequences: Optional[List[str]] = None
    model: str = OLLAMA_MODEL  # Allow overriding the default model

# Text generation endpoint using Ollama API
@app.post("/api/generate")
async def generate_text(request: TextRequest):
    if not is_ollama_ready:
        # Try to check status one more time
        ready = await check_ollama_status()
        if not ready:
            return {"error": "Ollama server is not available, please check if it's running"}

    # Log all available models for debugging
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            models_response = await client.get(f"{OLLAMA_API_BASE}/tags")
            if models_response.status_code == 200:
                available_models = models_response.json().get("models", [])
                model_names = [model.get("name") for model in available_models]
                logger.info(f"Available models: {model_names}")
            else:
                logger.error(f"Failed to get model list: {models_response.status_code}")
    except Exception as e:
        logger.error(f"Error checking available models: {str(e)}")
    
    logger.info(f"Received generation request for model: {request.model}")
    logger.info(f"Prompt preview: {request.prompt[:50]}...")
    
    # Check if the requested model exists, try to pull it if not
    model_exists = await ensure_model_exists(request.model)
    if not model_exists:
        return {
            "error": f"Model '{request.model}' not found and could not be pulled automatically. Please pull it manually with 'docker exec -it ollama ollama pull {request.model}'"
        }
    
    try:
        # Prepare the Ollama API request
        ollama_request = {
            "model": request.model,
            "prompt": request.prompt,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_new_tokens,  # Convert to Ollama's param
            },
            "stream": False  # Important: disable streaming to get a complete response
        }
        
        # Add stop sequences if provided
        if request.stop_sequences:
            ollama_request["options"]["stop"] = request.stop_sequences
        
        logger.info(f"Sending request to Ollama API with options: {ollama_request['options']}")
        
        # Send request to Ollama API
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{OLLAMA_API_BASE}/generate",
                    json=ollama_request
                )
                
                # Check if request was successful
                if response.status_code != 200:
                    error_msg = f"Ollama API returned status code: {response.status_code}"
                    logger.error(error_msg)
                    
                    # Try to extract error message from response
                    try:
                        error_details = response.json()
                        if "error" in error_details:
                            error_msg += f" - {error_details['error']}"
                    except:
                        pass
                        
                    return {"error": error_msg}
                
                # Handle both streaming and non-streaming responses
                if 'application/x-ndjson' in response.headers.get('content-type', ''):
                    # Process streaming response (even though we requested non-streaming)
                    logger.info("Received streaming response despite requesting non-streaming")
                    full_text = await process_streaming_response(response.text)
                    logger.info(f"Processed streaming response, length: {len(full_text)}")
                else:
                    # Process normal JSON response
                    response_data = response.json()
                    full_text = response_data.get("response", "")
                
                # Calculate approximate token counts
                # This is an estimate since we don't have exact token counts
                prompt_tokens = len(request.prompt.split()) // 3 * 4  # Rough estimate
                completion_tokens = len(full_text.split()) // 3 * 4   # Rough estimate
                total_tokens = prompt_tokens + completion_tokens
                
                logger.info(f"Successfully generated text: {len(full_text)} characters")
                
                return {
                    "text": full_text,
                    "model": request.model,
                    "usage": {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": total_tokens
                    }
                }
                
            except httpx.TimeoutException:
                logger.error("Request to Ollama API timed out")
                return {"error": "Generation timed out. Try using a smaller max_new_tokens value or a lighter model."}
                
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(error_trace)
        return {"error": str(e)}

# Function to process streaming responses
async def process_streaming_response(text_stream):
    """Process Ollama streaming response format and extract the generated text."""
    full_text = ""
    
    # Process each line of the stream
    for line in text_stream.strip().split('\n'):
        if not line:
            continue
            
        try:
            # Parse the JSON line
            data = json.loads(line)
            
            # Extract the response fragment
            if "response" in data:
                full_text += data["response"]
                
            # Check if this is the last message
            if data.get("done", False):
                break
                
        except json.JSONDecodeError:
            logger.warning(f"Failed to decode JSON line: {line}")
            
    return full_text

# Function to check if Ollama is running and check available models
async def check_ollama_status():
    global is_ollama_ready
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_API_BASE}/tags")
            if response.status_code == 200:
                is_ollama_ready = True
                logger.info("Ollama server is ready")
                
                # Log available models
                models = response.json().get("models", [])
                model_names = [model.get("name") for model in models]
                logger.info(f"Available Ollama models: {model_names}")
                return True
            else:
                logger.error(f"Ollama server returned status code: {response.status_code}")
                return False
    except Exception as e:
        logger.error(f"Error connecting to Ollama: {str(e)}")
        return False

# Function to check if a model exists and pull it if it doesn't
async def ensure_model_exists(model_name: str):
    logger.info(f"Checking if model '{model_name}' exists")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Check available models
            response = await client.get(f"{OLLAMA_API_BASE}/tags")
            if response.status_code != 200:
                logger.error(f"Failed to get model list: {response.status_code}")
                return False
            
            models = response.json().get("models", [])
            model_names = [model.get("name") for model in models]
            
            # If model doesn't exist, pull it
            if model_name not in model_names:
                logger.info(f"Model '{model_name}' not found, pulling it now...")
                
                # Start the pull operation
                pull_response = await client.post(
                    f"{OLLAMA_API_BASE}/pull",
                    json={"name": model_name}
                )
                
                if pull_response.status_code != 200:
                    logger.error(f"Failed to start model pull: {pull_response.status_code}")
                    return False
                
                logger.info(f"Started pulling model '{model_name}'")
                return True
            else:
                logger.info(f"Model '{model_name}' already exists")
                return True
    except Exception as e:
        logger.error(f"Error ensuring model exists: {str(e)}")
        return False

# Startup event to check if Ollama is ready
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Ollama API connector")
    status = await check_ollama_status()
    
    # Pull the default model if Ollama is ready
    if status and is_ollama_ready:
        await ensure_model_exists(OLLAMA_MODEL)
    
    # Periodically check Ollama status
    asyncio.create_task(periodic_status_check())

async def periodic_status_check():
    while True:
        if not is_ollama_ready:
            await check_ollama_status()
        await asyncio.sleep(30)  # Check every 30 seconds if not ready