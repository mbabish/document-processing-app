from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging
from typing import Optional, List

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Simple LLM API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Define model parameters - using a smaller DeepSeek model
MODEL_ID = "deepseek-ai/deepseek-coder-1.3b-base"  # A much smaller model
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
LOAD_8BIT = DEVICE == "cuda"  # Use 8-bit quantization if on CUDA

# Global model and tokenizer objects
model = None
tokenizer = None

# Model loading status
is_model_loaded = False

class TextRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 512
    temperature: float = 0.7
    stop_sequences: Optional[List[str]] = None

def load_model_in_background():
    global model, tokenizer, is_model_loaded
    
    try:
        logger.info(f"Loading model {MODEL_ID} on {DEVICE}")
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        
        # Load model with quantization if on CUDA
        if LOAD_8BIT:
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_ID,
                device_map="auto",
                load_in_8bit=True,
                torch_dtype=torch.float16
            )
        else:
            model = AutoModelForCausalLM.from_pretrained(MODEL_ID)
            model.to(DEVICE)
        
        is_model_loaded = True
        logger.info("Model loaded successfully")
    
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        is_model_loaded = False

@app.on_event("startup")
async def startup_event():
    # Start loading the model in the background
    background_tasks = BackgroundTasks()
    background_tasks.add_task(load_model_in_background)
    await background_tasks()

@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Simple LLM API is running",
        "model_loaded": is_model_loaded,
        "model_id": MODEL_ID,
        "device": DEVICE
    }

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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
