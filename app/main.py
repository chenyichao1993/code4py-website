from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import replicate

app = FastAPI(title="Code4Py API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Replicate
replicate_token = os.getenv("REPLICATE_API_TOKEN")
print(f"Replicate token found: {replicate_token is not None}")
print(f"Token preview: {replicate_token[:10] if replicate_token else 'None'}...")

if replicate_token:
    replicate_client = replicate.Client(api_token=replicate_token)
    print("✅ Replicate client initialized")
else:
    print("❌ No Replicate token")
    replicate_client = None

class Request(BaseModel):
    prompt: str

@app.get("/health")
async def health():
    return {
        "status": "ok", 
        "replicate_available": replicate_client is not None,
        "token_preview": replicate_token[:10] if replicate_token else "None"
    }

@app.post("/api/generate")
async def generate(request: Request):
    try:
        print(f"Generate request: {request.prompt}")
        
        if not replicate_client:
            return {"code": "# Error: Replicate not available", "execution_time": 0}
        
        # Use OpenAI GPT-4o-mini with optimized prompt
        system_prompt = """You are a Python expert. Convert natural language descriptions into clean, working Python code.

Requirements:
- Write complete, functional Python code
- Add clear comments
- Follow Python best practices
- Include usage examples
- Return only code, no explanations"""

        response = replicate_client.run(
            "openai/gpt-4o-mini",
            input={
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": request.prompt
                    }
                ],
                "max_tokens": 1200,
                "temperature": 0.1,
                "top_p": 0.9
            }
        )
        
        result = ""
        chunk_count = 0
        for chunk in response:
            result += str(chunk)
            chunk_count += 1
        
        print(f"Generated: {len(result)} characters, {chunk_count} chunks")
        return {"code": result, "execution_time": 1.0}
    
    except Exception as e:
        print(f"Error: {e}")
        return {"code": f"# Error: {str(e)}", "execution_time": 0}

@app.post("/api/convert")
async def convert(request: Request):
    try:
        print(f"Convert request: {request.prompt}")
        
        if not replicate_client:
            return {"code": "# Error: Replicate not available", "execution_time": 0}
        
        system_prompt = """You are a code conversion expert. Convert the given code to Python while maintaining the same functionality.

Requirements:
- Keep exact same functionality
- Use proper Python syntax
- Add comments for major changes
- Return only the converted code"""

        response = replicate_client.run(
            "openai/gpt-4o-mini",
            input={
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": request.prompt
                    }
                ],
                "max_tokens": 1200,
                "temperature": 0.1,
                "top_p": 0.9
            }
        )
        
        result = ""
        for chunk in response:
            result += str(chunk)
        
        return {"code": result, "execution_time": 1.0}
    
    except Exception as e:
        print(f"Error: {e}")
        return {"code": f"# Error: {str(e)}", "execution_time": 0}

@app.post("/api/explain")
async def explain(request: Request):
    try:
        print(f"Explain request: {request.prompt}")
        
        if not replicate_client:
            return {"code": "# Error: Replicate not available", "execution_time": 0}
        
        system_prompt = """You are a code analyst. Explain the given Python code clearly and concisely.

Provide:
- What the code does
- How it works
- Key concepts used
- Potential issues
- Improvement suggestions

Keep explanations simple and practical."""

        response = replicate_client.run(
            "openai/gpt-4o-mini",
            input={
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": request.prompt
                    }
                ],
                "max_tokens": 1200,
                "temperature": 0.1,
                "top_p": 0.9
            }
        )
        
        result = ""
        for chunk in response:
            result += str(chunk)
        
        return {"code": result, "execution_time": 1.0}
    
    except Exception as e:
        print(f"Error: {e}")
        return {"code": f"# Error: {str(e)}", "execution_time": 0}

@app.post("/api/debug")
async def debug(request: Request):
    try:
        print(f"Debug request: {request.prompt}")
        
        if not replicate_client:
            return {"code": "# Error: Replicate not available", "execution_time": 0}
        
        system_prompt = """You are a Python debugger. Find and fix issues in the given code.

Requirements:
- Identify all bugs and errors
- Provide corrected code
- Explain what was wrong
- Suggest improvements

Focus on making the code work correctly."""

        response = replicate_client.run(
            "openai/gpt-4o-mini",
            input={
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": request.prompt
                    }
                ],
                "max_tokens": 1200,
                "temperature": 0.1,
                "top_p": 0.9
            }
        )
        
        result = ""
        for chunk in response:
            result += str(chunk)
        
        return {"code": result, "execution_time": 1.0}
    
    except Exception as e:
        print(f"Error: {e}")
        return {"code": f"# Error: {str(e)}", "execution_time": 0}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)