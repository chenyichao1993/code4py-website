#!/usr/bin/env python3
"""
创建正确的.env文件
"""

def create_env_file():
    """创建.env文件"""
    env_content = """# OpenRouter Configuration
OPENROUTER_API_KEY=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
OPENROUTER_API_BASE=https://openrouter.ai/api/v1

# Database Configuration (暂时可以留空，后续配置)
DATABASE_URL=postgresql://username:password@localhost:5432/code4py_db
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# JWT Configuration
SECRET_KEY=your_very_secure_secret_key_here_change_this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ .env文件创建成功！")
        return True
    except Exception as e:
        print(f"❌ 创建.env文件失败：{e}")
        return False

if __name__ == "__main__":
    create_env_file()

