#!/usr/bin/env python3
"""
测试您的OpenRouter API密钥
"""

import openai
import os

def test_your_api_key():
    print("🚀 测试您的OpenRouter API密钥")
    print("=" * 50)
    
    # 您的API密钥
    api_key = "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"
    
    # 设置OpenRouter客户端
    openai.api_key = api_key
    openai.api_base = "https://openrouter.ai/api/v1"
    
    try:
        print("🔄 正在测试API连接...")
        
        # 测试API调用
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "请回复'测试成功'"}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ API测试成功！")
        print(f"📝 响应：{result}")
        
        # 显示费用信息
        if 'usage' in response:
            usage = response['usage']
            print(f"📊 Token使用：{usage.get('total_tokens', 0)} tokens")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误：{str(e)}")
        return False

def test_code_generation():
    """测试代码生成功能"""
    
    print("\n🔄 正在测试代码生成功能...")
    
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
        print(f"❌ 代码生成测试失败：{str(e)}")
        return False

if __name__ == "__main__":
    success = test_your_api_key()
    
    if success:
        print("\n🎉 恭喜！您的API密钥配置成功！")
        test_code_generation()
        print("\n✅ 现在可以配置环境变量了")
    else:
        print("\n❌ API密钥测试失败，请检查网络连接")
    
    print("\n按Enter键退出...")
    input()

