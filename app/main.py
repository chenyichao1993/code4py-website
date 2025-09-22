from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import time
from datetime import datetime
import replicate

# Load environment variables
replicate_token = os.getenv("REPLICATE_API_TOKEN")

app = FastAPI(
    title="Code4Py API",
    description="AI Python Code Generator API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Replicate
if replicate_token:
    replicate_client = replicate.Client(api_token=replicate_token)
    print("Replicate client initialized successfully")
else:
    print("Warning: No Replicate API token found")
    replicate_client = None

# Pydantic models
class CodeGenerationRequest(BaseModel):
    prompt: str
    context: Optional[str] = None

class CodeResponse(BaseModel):
    code: str
    execution_time: float

# Simple API functions
async def generate_code_simple(prompt: str, context: str = None) -> str:
    """Generate Python code using Replicate API - Ultra simple version"""
    try:
        if not replicate_client:
            return "# Error: Replicate client not available"
        
        # Ultra simple prompt
        full_prompt = f"Write Python code for: {prompt}"
        if context:
            full_prompt += f"\nContext: {context}"
        
        print(f"Simple prompt: {full_prompt}")
        
        # Ultra simple API call
        response = replicate_client.run(
            "meta/llama-2-70b-chat",
            input={"prompt": full_prompt}
        )
        
        # Simple response handling
        result = ""
        for chunk in response:
            result += str(chunk)
        
        return result.strip()
        
    except Exception as e:
        print(f"Error: {e}")
        return f"# Error: {str(e)}\n\ndef main():\n    print('Hello World')\n\nif __name__ == '__main__':\n    main()"

# API endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/generate", response_model=CodeResponse)
async def generate_code(request: CodeGenerationRequest, http_request: Request):
    """Generate Python code from natural language"""
    try:
        print(f"Generate request: {request.prompt}")
        
        # Generate code
        generated_code = await generate_code_simple(request.prompt, request.context)
        
        return {
            "code": generated_code,
            "execution_time": 1.0
        }
    
    except Exception as e:
        print(f"Generate error: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/api/convert", response_model=CodeResponse)
async def convert_code(request: CodeGenerationRequest, http_request: Request):
    """Convert code from one language to Python"""
    try:
        print(f"Convert request: {request.prompt}")
        
        # Simple conversion
        converted_code = await generate_code_simple(f"Convert to Python: {request.prompt}")
        
        return {
            "code": converted_code,
            "execution_time": 1.0
        }
    
    except Exception as e:
        print(f"Convert error: {e}")
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

@app.post("/api/explain", response_model=CodeResponse)
async def explain_code(request: CodeGenerationRequest, http_request: Request):
    """Explain what Python code does"""
    try:
        print(f"Explain request: {request.prompt}")
        
        # Simple explanation
        explanation = await generate_code_simple(f"Explain this code: {request.prompt}")
        
        return {
            "code": explanation,
            "execution_time": 1.0
        }
    
    except Exception as e:
        print(f"Explain error: {e}")
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")

@app.post("/api/debug", response_model=CodeResponse)
async def debug_code(request: CodeGenerationRequest, http_request: Request):
    """Debug Python code"""
    try:
        print(f"Debug request: {request.prompt}")
        
        # Simple debugging
        debug_result = await generate_code_simple(f"Debug this code: {request.prompt}")
        
        return {
            "code": debug_result,
            "execution_time": 1.0
        }
    
    except Exception as e:
        print(f"Debug error: {e}")
        raise HTTPException(status_code=500, detail=f"Debugging failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
