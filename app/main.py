from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import replicate
from datetime import datetime

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
replicate_token = os.getenv("REPLICATE_API_TOKEN")
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

# Helper function to get real IP
def get_real_ip(request: Request) -> str:
    """Get real IP address from request"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

# AI Code Generation Functions
async def generate_code_with_replicate(prompt: str, context: str = None) -> str:
    """Generate Python code using Replicate API - Following official documentation"""
    try:
        if not replicate_client:
            raise Exception("Replicate client not initialized")
        
        # Build the prompt according to documentation
        if context:
            full_prompt = f"Generate Python code for: {prompt}\n\nContext: {context}"
        else:
            full_prompt = f"Generate Python code for: {prompt}"
        
        print(f"Calling Replicate with prompt: {full_prompt[:100]}...")
        
        # Use Replicate API exactly as documented
        # Backend handles formatting automatically, no need for [INST] tags
        response = replicate_client.run(
            "meta/llama-2-70b-chat",
            input={
                "prompt": full_prompt,
                "system_prompt": "You are a Python code generator. Generate clean, well-commented Python code that follows best practices."
            }
        )
        
        # Collect response chunks
        result = ""
        for chunk in response:
            result += str(chunk)
        
        print(f"Generated code length: {len(result)}")
        return result.strip()
        
    except Exception as e:
        print(f"Replicate API error: {e}")
        raise Exception(f"Code generation failed: {str(e)}")

async def convert_code_with_replicate(code: str, from_lang: str, to_lang: str) -> str:
    """Convert code from one language to Python using Replicate API"""
    try:
        if not replicate_client:
            raise Exception("Replicate client not initialized")
        
        prompt = f"Convert this {from_lang} code to {to_lang}:\n\n{code}"
        
        response = replicate_client.run(
            "meta/llama-2-70b-chat",
            input={
                "prompt": prompt,
                "system_prompt": f"You are a code converter. Convert {from_lang} code to {to_lang} while maintaining the same functionality."
            }
        )
        
        result = ""
        for chunk in response:
            result += str(chunk)
        
        return result.strip()
        
    except Exception as e:
        print(f"Code conversion error: {e}")
        raise Exception(f"Code conversion failed: {str(e)}")

async def explain_code_with_replicate(code: str, language: str) -> str:
    """Explain what code does using Replicate API"""
    try:
        if not replicate_client:
            raise Exception("Replicate client not initialized")
        
        prompt = f"Explain what this {language} code does:\n\n{code}"
        
        response = replicate_client.run(
            "meta/llama-2-70b-chat",
            input={
                "prompt": prompt,
                "system_prompt": "You are a code explainer. Provide clear, detailed explanations of what the code does, how it works, and its key concepts."
            }
        )
        
        result = ""
        for chunk in response:
            result += str(chunk)
        
        return result.strip()
        
    except Exception as e:
        print(f"Code explanation error: {e}")
        raise Exception(f"Code explanation failed: {str(e)}")

async def debug_code_with_replicate(code: str) -> str:
    """Debug Python code using Replicate API"""
    try:
        if not replicate_client:
            raise Exception("Replicate client not initialized")
        
        prompt = f"Debug this Python code and provide fixes:\n\n{code}"
        
        response = replicate_client.run(
            "meta/llama-2-70b-chat",
            input={
                "prompt": prompt,
                "system_prompt": "You are a Python debugger. Analyze the code for bugs, potential issues, and provide corrected versions with explanations."
            }
        )
        
        result = ""
        for chunk in response:
            result += str(chunk)
        
        return result.strip()
        
    except Exception as e:
        print(f"Code debugging error: {e}")
        raise Exception(f"Code debugging failed: {str(e)}")

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "replicate_available": replicate_client is not None
    }

@app.post("/api/generate", response_model=CodeResponse)
async def generate_code(request: CodeGenerationRequest, http_request: Request):
    """Generate Python code from natural language"""
    try:
        user_ip = get_real_ip(http_request)
        print(f"Generate request from {user_ip}: {request.prompt}")
        
        # Generate code using Replicate
        generated_code = await generate_code_with_replicate(request.prompt, request.context)
        
        return {
            "code": generated_code,
            "execution_time": 1.0
        }
    
    except Exception as e:
        print(f"Generate error: {e}")
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)}")

@app.post("/api/convert", response_model=CodeResponse)
async def convert_code(request: CodeGenerationRequest, http_request: Request):
    """Convert code from one language to Python"""
    try:
        user_ip = get_real_ip(http_request)
        print(f"Convert request from {user_ip}: {request.prompt}")
        
        # Extract language info from prompt (simple parsing)
        prompt_lower = request.prompt.lower()
        if "java" in prompt_lower:
            from_lang = "Java"
        elif "javascript" in prompt_lower:
            from_lang = "JavaScript"
        elif "c++" in prompt_lower or "cpp" in prompt_lower:
            from_lang = "C++"
        else:
            from_lang = "other language"
        
        converted_code = await convert_code_with_replicate(request.prompt, from_lang, "Python")
        
        return {
            "code": converted_code,
            "execution_time": 1.0
        }
    
    except Exception as e:
        print(f"Convert error: {e}")
        raise HTTPException(status_code=500, detail=f"Code conversion failed: {str(e)}")

@app.post("/api/explain", response_model=CodeResponse)
async def explain_code(request: CodeGenerationRequest, http_request: Request):
    """Explain what Python code does"""
    try:
        user_ip = get_real_ip(http_request)
        print(f"Explain request from {user_ip}: {request.prompt}")
        
        explanation = await explain_code_with_replicate(request.prompt, "Python")
        
        return {
            "code": explanation,
            "execution_time": 1.0
        }
    
    except Exception as e:
        print(f"Explain error: {e}")
        raise HTTPException(status_code=500, detail=f"Code explanation failed: {str(e)}")

@app.post("/api/debug", response_model=CodeResponse)
async def debug_code(request: CodeGenerationRequest, http_request: Request):
    """Debug Python code"""
    try:
        user_ip = get_real_ip(http_request)
        print(f"Debug request from {user_ip}: {request.prompt}")
        
        debug_result = await debug_code_with_replicate(request.prompt)
        
        return {
            "code": debug_result,
            "execution_time": 1.0
        }
    
    except Exception as e:
        print(f"Debug error: {e}")
        raise HTTPException(status_code=500, detail=f"Code debugging failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)