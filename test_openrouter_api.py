#!/usr/bin/env python3
"""
OpenRouter API 测试脚本
用于验证OpenRouter API密钥是否有效
"""

import openai
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_openrouter_api():
    """测试OpenRouter API连接"""
    
    # 获取API密钥
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        print("❌ 错误：未找到OPENROUTER_API_KEY环境变量")
        print("请确保在.env文件中设置了API密钥")
        return False
    
    if not api_key.startswith("sk-or-"):
        print("❌ 错误：API密钥格式不正确")
        print("OpenRouter API密钥应该以'sk-or-'开头")
        return False
    
    # 设置OpenRouter客户端
    openai.api_key = api_key
    openai.api_base = "https://openrouter.ai/api/v1"
    
    try:
        print("🔄 正在测试OpenRouter API连接...")
        
        # 测试简单的API调用
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",  # OpenRouter使用provider/model格式
            messages=[
                {"role": "user", "content": "Hello, please respond with 'OpenRouter API test successful'"}
            ],
            max_tokens=50
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ OpenRouter API测试成功！")
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
        print("请检查账户余额或购买更多credits")
        return False
        
    except Exception as e:
        print(f"❌ 未知错误：{str(e)}")
        return False

def test_code_generation():
    """测试代码生成功能"""
    
    print("\n🔄 正在测试代码生成功能...")
    
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

def list_available_models():
    """列出可用的模型"""
    
    print("\n🔄 正在获取可用模型列表...")
    
    try:
        # 注意：OpenRouter可能不支持这个端点，这里只是示例
        models = openai.Model.list()
        print("✅ 可用模型：")
        for model in models.data:
            print(f"   - {model.id}")
        return True
        
    except Exception as e:
        print(f"❌ 获取模型列表失败：{str(e)}")
        print("这是正常的，OpenRouter可能不支持此端点")
        return False

if __name__ == "__main__":
    print("🚀 OpenRouter API 测试工具")
    print("=" * 50)
    
    # 测试基本连接
    if test_openrouter_api():
        print("\n" + "=" * 50)
        # 测试代码生成
        test_code_generation()
        # 尝试获取模型列表
        list_available_models()
    
    print("\n" + "=" * 50)
    print("测试完成！")

