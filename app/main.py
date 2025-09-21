from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import os
from dotenv import load_dotenv
import openai
import redis
import json
from datetime import datetime, timedelta
import uuid

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

# Initialize OpenAI (支持OpenRouter)
openai.api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")

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

# OpenAI helper functions
async def generate_code_with_openai(prompt: str, context: str = None) -> str:
    """Generate Python code using OpenRouter API"""
    try:
        # 获取API配置
        api_key = os.getenv("OPENROUTER_API_KEY")
        api_base = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
        
        if not api_key:
            raise Exception("OpenRouter API key not found")
        
        # 创建OpenAI客户端
        client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=api_base
        )
        
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
        
        # 使用OpenRouter格式的模型名称
        model_name = "openai/gpt-3.5-turbo"
        
        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"OpenRouter API error: {e}")
        raise Exception(f"Code generation failed: {str(e)}")

async def convert_code_with_openai(code: str, from_lang: str, to_lang: str) -> str:
    """Convert code from one language to another"""
    try:
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
        
        # 获取API配置
        api_key = os.getenv("OPENROUTER_API_KEY")
        api_base = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
        
        if not api_key:
            raise Exception("OpenRouter API key not found")
        
        # 创建OpenAI客户端
        client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=api_base
        )
        
        # 使用OpenRouter格式的模型名称
        model_name = "openai/gpt-3.5-turbo"
        
        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": code}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code conversion failed: {str(e)}")

async def explain_code_with_openai(code: str, language: str) -> dict:
    """Explain and analyze code"""
    try:
        system_prompt = f"""You are an expert {language} developer and code analyst. Analyze the following code and provide a comprehensive explanation.

Provide:
1. **What the code does**: Clear, step-by-step explanation of functionality
2. **How it works**: Technical details of algorithms, data structures, and logic flow
3. **Key concepts**: Important programming concepts used
4. **Input/Output**: What inputs are expected and what outputs are produced
5. **Potential issues**: Any bugs, edge cases, or improvements needed
6. **Optimization suggestions**: Ways to improve performance or readability

Format your response as JSON with keys: explanation, how_it_works, key_concepts, input_output, issues, suggestions"""
        
        # 获取API配置
        api_key = os.getenv("OPENROUTER_API_KEY")
        api_base = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
        
        if not api_key:
            raise Exception("OpenRouter API key not found")
        
        # 创建OpenAI客户端
        client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=api_base
        )
        
        # 使用OpenRouter格式的模型名称
        model_name = "openai/gpt-3.5-turbo"
        
        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": code}
            ],
            max_tokens=1500,
            temperature=0.5
        )
        
        result = response.choices[0].message.content.strip()
        
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
        raise HTTPException(status_code=500, detail=f"Code analysis failed: {str(e)}")

async def debug_code_with_openai(code: str) -> dict:
    """Debug and fix Python code issues"""
    try:
        system_prompt = """You are an expert Python debugger and code fixer. Analyze the following code and identify all issues.

Requirements:
1. **Identify bugs**: Find syntax errors, logic errors, runtime errors, and potential issues
2. **Provide fixes**: Give corrected versions of problematic code sections
3. **Explain problems**: Clearly explain what was wrong and why
4. **Test cases**: Suggest test cases to verify the fixes
5. **Best practices**: Recommend improvements for code quality

Format your response as JSON with keys: bugs_found, fixed_code, explanations, test_cases, improvements

Focus on making the code robust, efficient, and maintainable."""
        
        # 获取API配置
        api_key = os.getenv("OPENROUTER_API_KEY")
        api_base = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
        
        if not api_key:
            raise Exception("OpenRouter API key not found")
        
        # 创建OpenAI客户端
        client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=api_base
        )
        
        # 使用OpenRouter格式的模型名称
        model_name = "openai/gpt-3.5-turbo"
        
        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": code}
            ],
            max_tokens=2000,
            temperature=0.3
        )
        
        result = response.choices[0].message.content.strip()
        
        try:
            analysis = json.loads(result)
            return analysis
        except:
            return {
                "bugs_found": ["Unable to parse AI response"],
                "fixed_code": code,
                "explanations": ["AI response was not in valid JSON format"],
                "test_cases": [],
                "improvements": []
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code debugging failed: {str(e)}")

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
        # 使用真实的OpenRouter API生成代码
        generated_code = await generate_code_with_openai(request.prompt, request.context)
        
        print(f"AI生成代码长度: {len(generated_code)}")
        return {
            "code": generated_code,
            "execution_time": 0.5
        }
    
    except Exception as e:
        print(f"AI生成失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 如果AI生成失败，返回错误信息
        return {
            "error": f"AI生成失败: {str(e)}",
            "code": None,
            "execution_time": 0.1
        }

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
        converted_code = await convert_code_with_openai(
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
        analysis = await explain_code_with_openai(request.code, request.language)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return CodeResponse(
            code=request.code,
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
        analysis = await debug_code_with_openai(request.code)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return CodeResponse(
            code=analysis.get("fixed_code", request.code),
            explanation=analysis.get("explanations", ["No issues found"]),
            suggestions=analysis.get("improvements", []),
            execution_time=execution_time
        )
    
    except Exception as e:
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

