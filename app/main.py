from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import os
import time
from dotenv import load_dotenv
import redis
import json
from datetime import datetime, timedelta
import uuid
import replicate

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Code4Py API",
    description="AI Python Code Generator API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize Replicate
replicate_token = os.getenv("REPLICATE_API_TOKEN")
replicate_client = None
if replicate_token:
    replicate_client = replicate.Client(api_token=replicate_token)
    print("Replicate client initialized successfully")
else:
    print("Warning: No Replicate API token found")

# Initialize Redis (with fallback for free hosting)
try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        password=os.getenv("REDIS_PASSWORD"),
        decode_responses=True
    )
    # Test connection
    redis_client.ping()
    print("Redis connected successfully")
except Exception as e:
    print(f"Redis not available: {e}")
    redis_client = None

# Memory storage as fallback when Redis is unavailable
memory_storage = {}

def get_memory_value(key: str, default=None):
    """Get value from memory storage"""
    return memory_storage.get(key, default)

def set_memory_value(key: str, value, expire_seconds=None):
    """Set value in memory storage"""
    memory_storage[key] = value
    if expire_seconds:
        # Simple expiration using timestamp
        memory_storage[f"{key}_expire"] = time.time() + expire_seconds

def increment_memory_value(key: str, amount=1):
    """Increment value in memory storage"""
    current = memory_storage.get(key, 0)
    if isinstance(current, str):
        current = int(current)
    memory_storage[key] = current + amount
    return memory_storage[key]

def is_memory_expired(key: str) -> bool:
    """Check if memory key is expired"""
    expire_key = f"{key}_expire"
    if expire_key in memory_storage:
        return time.time() > memory_storage[expire_key]
    return False

def check_daily_usage_limit(user_ip: str, daily_key: str):
    """Check and enforce daily usage limit with Redis or memory fallback"""
    whitelist_ips = ["127.0.0.1", "::1"]
    if user_ip in whitelist_ips:
        return  # Skip limit for whitelisted IPs
    
    if redis_client:
        # Use Redis
        current_usage = redis_client.get(daily_key)
        if current_usage is None:
            current_usage = 0
        else:
            current_usage = int(current_usage)
        
        if current_usage >= 10:
            raise HTTPException(
                status_code=429, 
                detail="Daily usage limit exceeded. You have used all 10 free generations today. Please try again tomorrow."
            )
        
        redis_client.incr(daily_key)
        redis_client.expire(daily_key, 86400)
        print(f"用户 {user_ip} 今日使用次数: {current_usage + 1}/10")
    else:
        # Use memory storage
        if is_memory_expired(daily_key):
            memory_storage.pop(daily_key, None)
            memory_storage.pop(f"{daily_key}_expire", None)
        
        current_usage = get_memory_value(daily_key, 0)
        if isinstance(current_usage, str):
            current_usage = int(current_usage)
        
        if current_usage >= 10:
            raise HTTPException(
                status_code=429, 
                detail="Daily usage limit exceeded. You have used all 10 free generations today. Please try again tomorrow."
            )
        
        new_usage = increment_memory_value(daily_key)
        set_memory_value(daily_key, new_usage, 86400)
        print(f"用户 {user_ip} 今日使用次数: {new_usage}/10 (内存存储)")

# Security
security = HTTPBearer(auto_error=False)

# Pydantic models
class CodeGenerationRequest(BaseModel):
    prompt: str
    language: Optional[str] = "python"
    context: Optional[str] = None

class CodeConversionRequest(BaseModel):
    code: str
    from_language: str
    to_language: str = "python"

class CodeExplanationRequest(BaseModel):
    code: str
    language: str = "python"

class CodeResponse(BaseModel):
    code: str
    explanation: Optional[str] = None
    suggestions: Optional[List[str]] = None
    execution_time: Optional[float] = None

class UserRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    subscription_type: str
    created_at: datetime

# Core AI functions

# Get real IP address
def get_real_ip(request: Request) -> str:
    """Get the real IP address from request"""
    # Check for forwarded IP (when behind proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to client host
    return request.client.host

# Daily usage limit decorator
def daily_usage_limit(key: str, limit: int = 10):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_date = datetime.now().strftime("%Y-%m-%d")
            daily_key = f"daily_usage:{key}:{current_date}"
            
            # Check if user is in whitelist (for testing)
            whitelist_ips = ["127.0.0.1", "::1"]  # Add your IP here
            if key in whitelist_ips:
                return await func(*args, **kwargs)
            
            # Check daily usage
            if redis_client:
                current_usage = redis_client.get(daily_key)
                if current_usage is None:
                    current_usage = 0
                else:
                    current_usage = int(current_usage)
                
                if current_usage >= limit:
                    raise HTTPException(
                        status_code=429, 
                        detail="Daily usage limit exceeded. You have used all 10 free generations today. Please try again tomorrow."
                    )
                
                # Increment usage count
                redis_client.incr(daily_key)
                redis_client.expire(daily_key, 86400)  # Expire at midnight
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Rate limiting decorator (for additional protection)
def rate_limit(key: str, limit: int = 10, window: int = 3600):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_time = datetime.now()
            window_start = current_time - timedelta(seconds=window)
            
            # Check rate limit
            if redis_client:
                user_requests = redis_client.zrangebyscore(
                    f"rate_limit:{key}", 
                    window_start.timestamp(), 
                    current_time.timestamp()
                )
                
                if len(user_requests) >= limit:
                    raise HTTPException(
                        status_code=429, 
                        detail="Rate limit exceeded. Please try again later."
                    )
                
                # Add current request
                redis_client.zadd(f"rate_limit:{key}", {str(uuid.uuid4()): current_time.timestamp()})
                redis_client.expire(f"rate_limit:{key}", window)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Dependency to get current user (simplified for demo)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        return {"id": "anonymous", "subscription_type": "free"}
    
    # In a real app, validate JWT token here
    return {"id": "user_123", "subscription_type": "premium"}

# Replicate helper functions
async def generate_code_with_replicate(prompt: str, context: str = None) -> str:
    """Generate Python code using Replicate API"""
    try:
        if not replicate_token:
            raise Exception("Replicate API token not found")
        
        if not replicate_client:
            raise Exception("Replicate client not initialized")
        
        # Use a more reliable model for code generation
        model_name = "meta/llama-2-70b-chat"
        
        # Format prompt according to Llama-2 chat format
        if context:
            formatted_prompt = f"[INST] Context: {context}\n\nRequest: {prompt} [/INST]"
        else:
            formatted_prompt = f"[INST] {prompt} [/INST]"
        
        # Use Replicate API with proper Llama-2 format
        response = replicate_client.run(
            model_name,
            input={
                "prompt": formatted_prompt,
                "max_new_tokens": 1000,
                "temperature": 0.1,
                "top_p": 0.9,
                "stop_sequences": ["[/INST]"]
            }
        )
        
        # Wait for the response to complete
        if hasattr(response, '__iter__'):
            # For async generators, collect all chunks
            result_chunks = []
            for chunk in response:
                result_chunks.append(str(chunk))
            response = ''.join(result_chunks)
        
        # Wait for the response to complete
        if hasattr(response, '__iter__'):
            # For async generators, collect all chunks
            result_chunks = []
            for chunk in response:
                result_chunks.append(str(chunk))
            response = ''.join(result_chunks)
        
        # Handle different response types from Replicate
        print(f"Response type: {type(response)}")
        print(f"Response content preview: {str(response)[:200]}...")
        
        if isinstance(response, list):
            # If response is a list, join the elements properly
            if len(response) == 1 and isinstance(response[0], str):
                # Single string in list
                result = response[0].strip()
            else:
                # Multiple elements, join with spaces
                result = ' '.join(str(item) for item in response)
            print(f"Converted list to string: {result[:100]}...")
            return result
        elif isinstance(response, str):
            result = response.strip()
            print(f"String response: {result[:100]}...")
            return result
        else:
            result = str(response)
            print(f"Other type response: {result[:100]}...")
            return result
    
    except Exception as e:
        print(f"Replicate API error: {e}")
        print(f"Error type: {type(e)}")
        print(f"Error details: {str(e)}")
        
        # Return a more helpful fallback response
        return f"""# Code Generation Failed

**Error:** {str(e)}

**Troubleshooting:**
1. Check if Replicate API token is valid
2. Verify internet connection
3. Ensure sufficient credits in Replicate account
4. Try again in a few minutes

**Fallback Example:**
```python
def example_function():
    # Your code here
    pass
```"""

async def convert_code_with_replicate(code: str, from_lang: str, to_lang: str) -> str:
    """Convert code from one language to another using Replicate"""
    try:
        if not replicate_token:
            raise Exception("Replicate API token not found")
        
        if not replicate_client:
            raise Exception("Replicate client not initialized")
        
        model_name = "meta/llama-2-70b-chat"
        
        formatted_prompt = f"[INST] Convert this {from_lang} code to {to_lang}. Maintain exact same functionality and logic, adapt to {to_lang} syntax and conventions, include proper error handling, follow {to_lang} best practices, preserve variable names and structure when possible, add comments explaining any significant changes. Return only the converted code:\n\n{code} [/INST]"
        
        response = replicate_client.run(
            model_name,
            input={
                "prompt": formatted_prompt,
                "max_new_tokens": 1000,
                "temperature": 0.1,
                "top_p": 0.9,
                "stop_sequences": ["[/INST]"]
            }
        )
        
        # Wait for the response to complete
        if hasattr(response, '__iter__'):
            # For async generators, collect all chunks
            result_chunks = []
            for chunk in response:
                result_chunks.append(str(chunk))
            response = ''.join(result_chunks)
        
        # Handle different response types from Replicate
        if isinstance(response, list):
            if len(response) == 1 and isinstance(response[0], str):
                return response[0].strip()
            else:
                return ' '.join(str(item) for item in response)
        elif isinstance(response, str):
            return response.strip()
        else:
            return str(response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code conversion failed: {str(e)}")

async def explain_code_with_replicate(code: str, language: str) -> dict:
    """Explain and analyze code using Replicate"""
    try:
        if not replicate_token:
            raise Exception("Replicate API token not found")
        
        if not replicate_client:
            raise Exception("Replicate client not initialized")
        
        model_name = "meta/llama-2-70b-chat"
        
        formatted_prompt = f"[INST] Explain what this {language} code does. Provide a clear, readable explanation covering: what the code does, how it works, key concepts, input/output, potential issues, and optimization suggestions. Format as plain text with clear sections, not JSON:\n\n{code} [/INST]"
        
        response = replicate_client.run(
            model_name,
            input={
                "prompt": formatted_prompt,
                "max_new_tokens": 1000,
                "temperature": 0.1,
                "top_p": 0.9,
                "stop_sequences": ["[/INST]"]
            }
        )
        
        # Wait for the response to complete
        if hasattr(response, '__iter__'):
            # For async generators, collect all chunks
            result_chunks = []
            for chunk in response:
                result_chunks.append(str(chunk))
            response = ''.join(result_chunks)
        
        # Handle different response types from Replicate
        if isinstance(response, list):
            result = '\n'.join(str(item) for item in response)
        elif isinstance(response, str):
            result = response.strip()
        else:
            result = str(response)
        
        # Return plain text explanation
            return {
                "explanation": result,
            "how_it_works": "See explanation above",
            "key_concepts": [],
            "input_output": "See explanation above", 
                "issues": [],
                "suggestions": []
            }
    
    except Exception as e:
        print(f"Explain code error: {e}")
        return {
            "explanation": f"Unable to explain code due to an error: {str(e)}",
            "how_it_works": "Error occurred during analysis",
            "key_concepts": [],
            "input_output": "Unable to determine",
            "issues": [f"Error: {str(e)}"],
            "suggestions": []
        }

async def debug_code_with_replicate(code: str) -> str:
    """Debug and fix Python code issues using Replicate"""
    try:
        if not replicate_token:
            return f"""**Debug Analysis Failed**

**Error:** Replicate API token not found. Please check your environment variables.

**Original Code:**
```python
{code}
```

**Setup Required:**
1. Set REPLICATE_API_TOKEN environment variable
2. Ensure you have a valid Replicate API token
3. Restart the application

**Unable to perform debugging analysis due to missing API configuration.**"""
        
        if not replicate_client:
            raise Exception("Replicate client not initialized")
        
        model_name = "meta/llama-2-70b-chat"
        
        formatted_prompt = f"[INST] Debug this Python code. Analyze and provide: issues found (list any bugs, potential problems, or improvements needed), fixed code (provide an improved version), explanation (explain what was wrong and how fixes improve the code), best practices (suggest additional improvements). Format as clear, readable text with sections marked with **bold headers**:\n\n{code} [/INST]"
        
        response = replicate_client.run(
            model_name,
            input={
                "prompt": formatted_prompt,
                "max_new_tokens": 1000,
                "temperature": 0.1,
                "top_p": 0.9,
                "stop_sequences": ["[/INST]"]
            }
        )
        
        # Wait for the response to complete
        if hasattr(response, '__iter__'):
            # For async generators, collect all chunks
            result_chunks = []
            for chunk in response:
                result_chunks.append(str(chunk))
            response = ''.join(result_chunks)
        
        # Handle different response types from Replicate
        if isinstance(response, list):
            if len(response) == 1 and isinstance(response[0], str):
                return response[0].strip()
            else:
                return ' '.join(str(item) for item in response)
        elif isinstance(response, str):
            return response.strip()
        else:
            return str(response)
    
    except Exception as e:
        print(f"Debug code error: {e}")
        error_msg = str(e)
        
        # Provide more specific error messages
        if "401" in error_msg or "User not found" in error_msg:
            error_msg = "Invalid API token. Please check your Replicate API token configuration."
        elif "429" in error_msg:
            error_msg = "API rate limit exceeded. Please try again later."
        elif "timeout" in error_msg.lower():
            error_msg = "Request timeout. Please try again."
        
        return f"""**Debug Analysis Failed**

**Error:** {error_msg}

**Original Code:**
```python
{code}
```

**Troubleshooting:**
1. Check your API token configuration
2. Verify your internet connection
3. Try again in a few moments

**Unable to perform debugging analysis due to an error. Please try again later.**"""

# API Routes
@app.get("/")
async def root():
    return {"message": "Code4Py API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/generate")
async def generate_code(request: CodeGenerationRequest, http_request: Request):
    """Generate Python code from natural language description"""
    print(f"收到请求: {request.prompt}")
    
    # Get real IP address
    user_ip = get_real_ip(http_request)
    print(f"用户IP: {user_ip}")
    
    # Check daily usage limit
    current_date = datetime.now().strftime("%Y-%m-%d")
    daily_key = f"daily_usage:{user_ip}:{current_date}"
    check_daily_usage_limit(user_ip, daily_key)
    
    try:
        # Use Replicate for code generation
        generated_code = await generate_code_with_replicate(request.prompt, request.context)
        print(f"Replicate generated code length: {len(generated_code)}")
        
        return {
            "code": generated_code,
            "execution_time": 0.5
        }
    
    except Exception as e:
        print(f"AI generation failed: {e}")
        import traceback
        traceback.print_exc()
        
        # If AI generation fails, raise HTTPException for consistent error handling
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@app.post("/api/convert", response_model=CodeResponse)
async def convert_code(request: CodeConversionRequest, http_request: Request):
    """Convert code from one language to Python"""
    # Get real IP address and check daily limit
    user_ip = get_real_ip(http_request)
    current_date = datetime.now().strftime("%Y-%m-%d")
    daily_key = f"daily_usage:{user_ip}:{current_date}"
    
    # Check if user is in whitelist (for testing)
    whitelist_ips = ["127.0.0.1", "::1"]
    if user_ip not in whitelist_ips and redis_client:
        current_usage = redis_client.get(daily_key)
        if current_usage is None:
            current_usage = 0
        else:
            current_usage = int(current_usage)
        
            if current_usage >= 10:
                raise HTTPException(
                    status_code=429, 
                    detail="Daily usage limit exceeded. You have used all 10 free generations today. Please try again tomorrow."
                )
        
        redis_client.incr(daily_key)
        redis_client.expire(daily_key, 86400)
    
    start_time = datetime.now()
    
    try:
        converted_code = await convert_code_with_replicate(
            request.code, 
            request.from_language, 
            request.to_language
        )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return CodeResponse(
            code=converted_code,
            execution_time=execution_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/explain", response_model=CodeResponse)
async def explain_code(request: CodeExplanationRequest, http_request: Request):
    """Explain and analyze Python code"""
    # Get real IP address and check daily limit
    user_ip = get_real_ip(http_request)
    current_date = datetime.now().strftime("%Y-%m-%d")
    daily_key = f"daily_usage:{user_ip}:{current_date}"
    
    # Check if user is in whitelist (for testing)
    whitelist_ips = ["127.0.0.1", "::1"]
    if user_ip not in whitelist_ips and redis_client:
        current_usage = redis_client.get(daily_key)
        if current_usage is None:
            current_usage = 0
        else:
            current_usage = int(current_usage)
        
            if current_usage >= 10:
                raise HTTPException(
                    status_code=429, 
                    detail="Daily usage limit exceeded. You have used all 10 free generations today. Please try again tomorrow."
                )
        
        redis_client.incr(daily_key)
        redis_client.expire(daily_key, 86400)
    
    start_time = datetime.now()
    
    try:
        analysis = await explain_code_with_replicate(request.code, request.language)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Format explanation as readable text
        explanation_text = f"""**What the code does:**
{analysis.get('explanation', 'No explanation available')}

**How it works:**
{analysis.get('how_it_works', 'No technical details available')}

**Key concepts:**
{', '.join(analysis.get('key_concepts', [])) if analysis.get('key_concepts') else 'No key concepts identified'}

**Input/Output:**
{analysis.get('input_output', 'No input/output information available')}

**Potential issues:**
{', '.join(analysis.get('issues', [])) if analysis.get('issues') else 'No issues identified'}

**Optimization suggestions:**
{', '.join(analysis.get('suggestions', [])) if analysis.get('suggestions') else 'No suggestions available'}"""

        return CodeResponse(
            code=explanation_text,
            explanation=analysis.get("explanation"),
            suggestions=analysis.get("suggestions", []),
            execution_time=execution_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/debug", response_model=CodeResponse)
async def debug_code(request: CodeExplanationRequest, http_request: Request):
    """Debug and fix Python code issues"""
    # Get real IP address and check daily limit
    user_ip = get_real_ip(http_request)
    current_date = datetime.now().strftime("%Y-%m-%d")
    daily_key = f"daily_usage:{user_ip}:{current_date}"
    
    check_daily_usage_limit(user_ip, daily_key)
    
    start_time = datetime.now()
    
    try:
        debug_analysis = await debug_code_with_replicate(request.code)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return CodeResponse(
            code=debug_analysis,
            explanation=["Debug analysis completed"],
            suggestions=[],
            execution_time=execution_time
        )
    
    except Exception as e:
        print(f"Debug endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# User management endpoints (simplified)
@app.post("/api/auth/register", response_model=UserResponse)
async def register_user(request: UserRequest):
    """Register a new user"""
    # In a real app, hash password and store in database
    user_id = str(uuid.uuid4())
    
    return UserResponse(
        id=user_id,
        email=request.email,
        name=request.name,
        subscription_type="free",
        created_at=datetime.now()
    )

@app.post("/api/auth/login")
async def login_user(request: UserRequest):
    """Login user and return JWT token"""
    # In a real app, verify password and return JWT
    return {
        "access_token": "dummy_token_for_demo",
        "token_type": "bearer",
        "user": {
            "id": "user_123",
            "email": request.email,
            "subscription_type": "free"
        }
    }

@app.get("/api/user/profile", response_model=UserResponse)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse(
        id=current_user["id"],
        email="user@example.com",
        name="Demo User",
        subscription_type=current_user["subscription_type"],
        created_at=datetime.now()
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

