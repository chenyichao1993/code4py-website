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
        
        # Simple API call
        response = replicate_client.run(
            "meta/llama-2-70b-chat",
            input={"prompt": f"Write Python code: {request.prompt}"}
        )
        
        result = ""
        for chunk in response:
            result += str(chunk)
        
        print(f"Generated: {len(result)} characters")
        return {"code": result, "execution_time": 1.0}
        
    except Exception as e:
        print(f"Error: {e}")
        return {"code": f"# Error: {str(e)}", "execution_time": 0}

@app.post("/api/convert")
async def convert(request: Request):
    return await generate(request)

@app.post("/api/explain")
async def explain(request: Request):
    return await generate(request)

@app.post("/api/debug")
async def debug(request: Request):
    return await generate(request)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)