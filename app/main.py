from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import os
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
        api_token = os.getenv("REPLICATE_API_TOKEN")
        if not api_token:
            raise Exception("Replicate API token not found")
        
        client = replicate_client
        if not client:
            raise Exception("Replicate client not initialized")
        
        system_prompt = """You are an expert Python developer. Generate clean, production-ready Python code based on the user's natural language description. 

Requirements:
- Write complete, functional Python code
- Include proper error handling and input validation
- Add clear comments and docstrings
- Follow Python best practices and PEP 8 style
- Include usage examples if appropriate
- Return only the code without explanations unless specifically asked

Focus on creating practical, efficient solutions that solve the user's problem."""
        
        user_prompt = prompt
        if context:
            user_prompt = f"Context: {context}\n\nRequest: {prompt}"
        
        # Use OpenAI GPT-4o Mini for cost-effective code generation
        model_name = "openai/gpt-4o-mini"
        
        response = client.run(
            model_name,
            input={
                "prompt": f"{system_prompt}\n\nUser: {user_prompt}\n\nAssistant:",
                "max_new_tokens": 2000,
                "temperature": 0.7
            }
        )
        
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
        # Return a fallback response instead of raising exception
        return f"""# Code Generation Failed

**Error:** {str(e)}

**Please try again later or contact support if the issue persists.**

**Fallback Example:**
```python
def example_function():
    # Your code here
    pass
```"""

async def convert_code_with_replicate(code: str, from_lang: str, to_lang: str) -> str:
    """Convert code from one language to another using Replicate"""
    try:
        api_token = os.getenv("REPLICATE_API_TOKEN")
        if not api_token:
            raise Exception("Replicate API token not found")
        
        client = replicate_client
        if not client:
            raise Exception("Replicate client not initialized")
        
        system_prompt = f"""You are an expert programmer specializing in code conversion. Convert the following {from_lang} code to {to_lang} code.

Requirements:
- Maintain exact same functionality and logic
- Adapt to {to_lang} syntax and conventions
- Include proper error handling
- Follow {to_lang} best practices
- Preserve variable names and structure when possible
- Add comments explaining any significant changes
- Return only the converted code

Ensure the converted code is functionally equivalent to the original."""
        
        model_name = "openai/gpt-4o-mini"
        
        response = client.run(
            model_name,
            input={
                "prompt": f"{system_prompt}\n\nCode to convert:\n{code}\n\nConverted {to_lang} code:",
                "max_new_tokens": 2000,
                "temperature": 0.3
            }
        )
        
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
        api_token = os.getenv("REPLICATE_API_TOKEN")
        if not api_token:
            raise Exception("Replicate API token not found")
        
        client = replicate_client
        if not client:
            raise Exception("Replicate client not initialized")
        
        system_prompt = f"""You are an expert {language} developer and code analyst. Analyze the following code and provide a comprehensive explanation.

Provide:
1. **What the code does**: Clear, step-by-step explanation of functionality
2. **How it works**: Technical details of algorithms, data structures, and logic flow
3. **Key concepts**: Important programming concepts used
4. **Input/Output**: What inputs are expected and what outputs are produced
5. **Potential issues**: Any bugs, edge cases, or improvements needed
6. **Optimization suggestions**: Ways to improve performance or readability

Format your response as JSON with keys: explanation, how_it_works, key_concepts, input_output, issues, suggestions"""
        
        model_name = "openai/gpt-4o-mini"
        
        response = client.run(
            model_name,
            input={
                "prompt": f"{system_prompt}\n\nCode to analyze:\n{code}\n\nAnalysis:",
                "max_new_tokens": 1500,
                "temperature": 0.5
            }
        )
        
        # Handle different response types from Replicate
        if isinstance(response, list):
            result = '\n'.join(str(item) for item in response)
        elif isinstance(response, str):
            result = response.strip()
        else:
            result = str(response)
        
        # Try to parse as JSON, fallback to plain text
        try:
            return json.loads(result)
        except:
            return {
                "explanation": result,
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
        api_token = os.getenv("REPLICATE_API_TOKEN")
        if not api_token:
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
        
        client = replicate_client
        if not client:
            raise Exception("Replicate client not initialized")
        
        system_prompt = """You are an expert Python debugger. Analyze the following code and provide a comprehensive debugging analysis.

Please provide:
1. **Issues found**: List any bugs, potential problems, or improvements needed
2. **Fixed code**: Provide an improved version of the code
3. **Explanation**: Explain what was wrong and how the fixes improve the code
4. **Best practices**: Suggest any additional improvements

Format your response as clear, readable text with sections marked with **bold headers**. Do not use JSON format."""
        
        model_name = "openai/gpt-4o-mini"
        
        response = client.run(
            model_name,
            input={
                "prompt": f"{system_prompt}\n\nCode to debug:\n{code}\n\nDebug Analysis:",
                "max_new_tokens": 1500,
                "temperature": 0.3
            }
        )
        
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
    
    # Check if user is in whitelist (for testing)
    whitelist_ips = ["127.0.0.1", "::1"]  # Add your IP here
    if user_ip not in whitelist_ips and redis_client:
        # Check daily usage
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
        
        # Increment usage count
        redis_client.incr(daily_key)
        redis_client.expire(daily_key, 86400)  # Expire at midnight
        print(f"用户 {user_ip} 今日使用次数: {current_usage + 1}/10")
    
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
    uvicorn.run(app, host="0.0.0.0", port=8000)

