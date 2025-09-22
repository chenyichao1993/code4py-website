from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import replicate

app = FastAPI(title="Code4Py Test API")

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
    print("Replicate client initialized")
else:
    print("No Replicate token")
    replicate_client = None

class Request(BaseModel):
    prompt: str

@app.get("/health")
async def health():
    return {"status": "ok", "replicate_available": replicate_client is not None}

@app.post("/api/generate")
async def generate(request: Request):
    try:
        if not replicate_client:
            return {"code": "# Error: Replicate not available", "execution_time": 0}
        
        print(f"Generating for: {request.prompt}")
        
        # Ultra simple call
        response = replicate_client.run(
            "meta/llama-2-70b-chat",
            input={"prompt": f"Write Python code: {request.prompt}"}
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
