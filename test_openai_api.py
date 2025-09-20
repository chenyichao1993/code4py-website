#!/usr/bin/env python3
"""
OpenAI API 测试脚本
用于验证API密钥是否有效
"""

import openai
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_openai_api():
    """测试OpenAI API连接"""
    
    # 获取API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ 错误：未找到OPENAI_API_KEY环境变量")
        print("请确保在.env文件中设置了API密钥")
        return False
    
    if not api_key.startswith("sk-"):
        print("❌ 错误：API密钥格式不正确")
        print("API密钥应该以'sk-'开头")
        return False
    
    # 设置OpenAI客户端
    openai.api_key = api_key
    
    try:
        print("🔄 正在测试OpenAI API连接...")
        
        # 测试简单的API调用
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello, please respond with 'API test successful'"}
            ],
            max_tokens=50
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ API测试成功！")
        print(f"📝 响应内容：{result}")
        
        # 显示使用情况
        if 'usage' in response:
            usage = response['usage']
            print(f"📊 Token使用情况：")
            print(f"   - 输入tokens: {usage.get('prompt_tokens', 0)}")
            print(f"   - 输出tokens: {usage.get('completion_tokens', 0)}")
            print(f"   - 总计tokens: {usage.get('total_tokens', 0)}")
        
        return True
        
    except openai.error.AuthenticationError:
        print("❌ 认证失败：API密钥无效")
        print("请检查API密钥是否正确")
        return False
        
    except openai.error.RateLimitError:
        print("❌ 速率限制：请求过于频繁")
        print("请稍后再试")
        return False
        
    except openai.error.InsufficientQuota:
        print("❌ 配额不足：账户余额不足")
        print("请检查账户余额或添加付费方式")
        return False
        
    except Exception as e:
        print(f"❌ 未知错误：{str(e)}")
        return False

def test_code_generation():
    """测试代码生成功能"""
    
    print("\n🔄 正在测试代码生成功能...")
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
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
            max_tokens=500
        )
        
        code = response.choices[0].message.content.strip()
        print("✅ 代码生成测试成功！")
        print("📝 生成的代码：")
        print("-" * 50)
        print(code)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ 代码生成测试失败：{str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 OpenAI API 测试工具")
    print("=" * 50)
    
    # 测试基本连接
    if test_openai_api():
        print("\n" + "=" * 50)
        # 测试代码生成
        test_code_generation()
    
    print("\n" + "=" * 50)
    print("测试完成！")


