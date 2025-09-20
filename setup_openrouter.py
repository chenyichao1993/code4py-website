#!/usr/bin/env python3
"""
一键设置OpenRouter配置
"""

import os
import openai

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
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env文件创建成功！")
        return True
    except Exception as e:
        print(f"❌ 创建.env文件失败：{e}")
        return False

def test_api_key():
    """测试API密钥"""
    print("🔄 正在测试API密钥...")
    
    api_key = "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"
    openai.api_key = api_key
    openai.api_base = "https://openrouter.ai/api/v1"
    
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "请回复'测试成功'"}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ API测试成功！响应：{result}")
        
        if 'usage' in response:
            usage = response['usage']
            print(f"📊 Token使用：{usage.get('total_tokens', 0)} tokens")
        
        return True
        
    except Exception as e:
        print(f"❌ API测试失败：{e}")
        return False

def test_code_generation():
    """测试代码生成"""
    print("🔄 正在测试代码生成...")
    
    api_key = "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"
    openai.api_key = api_key
    openai.api_base = "https://openrouter.ai/api/v1"
    
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert Python developer. Generate clean, production-ready Python code."
                },
                {
                    "role": "user", 
                    "content": "Create a simple function that calculates the factorial of a number"
                }
            ],
            max_tokens=300
        )
        
        code = response.choices[0].message.content.strip()
        print("✅ 代码生成测试成功！")
        print("📝 生成的代码：")
        print("-" * 50)
        print(code)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ 代码生成测试失败：{e}")
        return False

def update_gitignore():
    """更新.gitignore文件"""
    try:
        # 检查.gitignore是否存在
        if os.path.exists('.gitignore'):
            with open('.gitignore', 'r') as f:
                content = f.read()
            
            if '.env' not in content:
                with open('.gitignore', 'a') as f:
                    f.write('\n# Environment variables\n.env\n')
                print("✅ .gitignore文件已更新")
            else:
                print("✅ .gitignore文件已包含.env")
        else:
            with open('.gitignore', 'w') as f:
                f.write('# Environment variables\n.env\n')
            print("✅ .gitignore文件已创建")
        
        return True
    except Exception as e:
        print(f"❌ 更新.gitignore失败：{e}")
        return False

def main():
    print("🚀 OpenRouter一键设置")
    print("=" * 50)
    
    # 1. 创建.env文件
    if create_env_file():
        print("✅ 步骤1：.env文件创建完成")
    else:
        print("❌ 步骤1：.env文件创建失败")
        return
    
    # 2. 更新.gitignore
    if update_gitignore():
        print("✅ 步骤2：.gitignore文件更新完成")
    else:
        print("❌ 步骤2：.gitignore文件更新失败")
    
    # 3. 测试API密钥
    if test_api_key():
        print("✅ 步骤3：API密钥测试通过")
    else:
        print("❌ 步骤3：API密钥测试失败")
        return
    
    # 4. 测试代码生成
    if test_code_generation():
        print("✅ 步骤4：代码生成测试通过")
    else:
        print("❌ 步骤4：代码生成测试失败")
    
    print("\n🎉 所有步骤完成！")
    print("现在可以启动后端服务了：")
    print("uvicorn app.main:app --reload")

if __name__ == "__main__":
    main()

