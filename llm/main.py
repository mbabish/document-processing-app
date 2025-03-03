from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/llm_service.log')
    ]
)
logger = logging.getLogger(__name__)

# Ensure the parent logger captures all logs
logging.getLogger().setLevel(logging.INFO)

# Critical startup logging
logger.info("Starting LLM Service Initialization")
logger.info(f"Python Version: {sys.version}")
logger.info(f"PyTorch Version: {torch.__version__}")

# Critical environment checks
logger.info("Checking environment variables and system configuration")
logger.info(f"CUDA Available: {torch.cuda.is_available()}")
logger.info(f"CUDA Device Count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    logger.info(f"Current CUDA Device: {torch.cuda.current_device()}")
    logger.info(f"CUDA Device Name: {torch.cuda.get_device_name(0)}")

app = FastAPI(title="LLM Service")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define model parameters
MODEL_ID = "deepseek-ai/deepseek-coder-1.3b-base"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
LOAD_8BIT = DEVICE == "cuda"

# Global model and tokenizer objects
model = None
tokenizer = None

# Model loading status
is_model_loaded = False

def load_model_in_background():
    global model, tokenizer, is_model_loaded
    
    try:
        logger.info(f"Attempting to load model {MODEL_ID} on {DEVICE}")
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        logger.info("Tokenizer loaded successfully")
        
        # Load model with quantization if on CUDA
        if LOAD_8BIT:
            logger.info("Loading model in 8-bit quantization")
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_ID,
                device_map="auto",
                load_in_8bit=True,
                torch_dtype=torch.float16
            )
        else:
            logger.info("Loading model in full precision")
            model = AutoModelForCausalLM.from_pretrained(MODEL_ID)
            model.to(DEVICE)
        
        is_model_loaded = True
        logger.info("Model loaded successfully")
    
    except Exception as e:
        logger.error(f"Critical error loading model: {str(e)}")
        logger.error(f"Full error traceback:", exc_info=True)
        is_model_loaded = False

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI application startup")
    # Start loading the model in the background
    background_tasks = BackgroundTasks()
    background_tasks.add_task(load_model_in_background)
    await background_tasks()

@app.get("/")
async def root():
    logger.info("Health check endpoint accessed")
    return {
        "status": "ok",
        "message": "LLM Service is running",
        "model_loaded": is_model_loaded,
        "model_id": MODEL_ID,
        "device": DEVICE
    }

class TextRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 512
    temperature: float = 0.7
    stop_sequences: Optional[List[str]] = None

@app.post("/api/generate")
async def generate_text(request: TextRequest):
    if not is_model_loaded:
        return {"error": "Model is still loading, please try again in a moment"}
    
    try:
        # Generate text based on the prompt
        inputs = tokenizer(request.prompt, return_tensors="pt").to(DEVICE)
        
        # Generate with specified parameters
        generation_config = {
            "max_new_tokens": request.max_new_tokens,
            "temperature": request.temperature,
            "do_sample": request.temperature > 0,
        }
        
        with torch.no_grad():
            outputs = model.generate(**inputs, **generation_config)
        
        # Decode the generated text
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Handle stop sequences if provided
        if request.stop_sequences:
            for stop_seq in request.stop_sequences:
                if stop_seq in generated_text:
                    generated_text = generated_text.split(stop_seq)[0]
        
        # For cleaner output, remove the prompt from the generated text if it appears at the beginning
        if generated_text.startswith(request.prompt):
            generated_text = generated_text[len(request.prompt):].lstrip()
        
        return {
            "text": generated_text,
            "model": MODEL_ID,
            "usage": {
                "prompt_tokens": len(inputs.input_ids[0]),
                "completion_tokens": len(outputs[0]) - len(inputs.input_ids[0]),
                "total_tokens": len(outputs[0])
            }
        }
    
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting LLM service directly")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")