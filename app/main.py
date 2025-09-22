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
        system_prompt = """You are an expert Python developer. Generate clean, production-ready Python code based on the user's natural language description. 

Requirements:
- Write complete, functional Python code
- Include proper error handling and input validation
- Add clear comments and docstrings
- Follow Python best practices and PEP 8 style
- Include usage examples if appropriate
- Return only the code without explanations unless specifically asked

Focus on creating practical, efficient solutions that solve the user's problem."""

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
        
        system_prompt = """You are an expert programmer specializing in code conversion. Convert the following code to Python code.

Requirements:
- Maintain exact same functionality and logic
- Adapt to Python syntax and conventions
- Include proper error handling
- Follow Python best practices
- Preserve variable names and structure when possible
- Add comments explaining any significant changes
- Return only the converted code

Ensure the converted code is functionally equivalent to the original."""

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
        
        system_prompt = """You are an expert Python developer and code analyst. Analyze the following code and provide a comprehensive explanation.

Provide:
1. **What the code does**: Clear, step-by-step explanation of functionality
2. **How it works**: Technical details of algorithms, data structures, and logic flow
3. **Key concepts**: Important programming concepts used
4. **Input/Output**: What inputs are expected and what outputs are produced
5. **Potential issues**: Any bugs, edge cases, or improvements needed
6. **Optimization suggestions**: Ways to improve performance or readability

Format your response as JSON with keys: explanation, how_it_works, key_concepts, input_output, issues, suggestions"""

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
        
        system_prompt = """You are an expert Python debugger and code fixer. Analyze the following code and identify all issues.

Requirements:
1. **Identify bugs**: Find syntax errors, logic errors, runtime errors, and potential issues
2. **Provide fixes**: Give corrected versions of problematic code sections
3. **Explain problems**: Clearly explain what was wrong and why
4. **Test cases**: Suggest test cases to verify the fixes
5. **Best practices**: Recommend improvements for code quality

Format your response as JSON with keys: bugs_found, fixed_code, explanations, test_cases, improvements

Focus on making the code robust, efficient, and maintainable."""

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