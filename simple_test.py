#!/usr/bin/env python3
"""
最简单的OpenRouter测试脚本
"""

import openai
import os

def simple_test():
    print("🚀 简单测试OpenRouter API")
    print("=" * 40)
    
    # 您的API密钥
    api_key = "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"
    
    try:
        # 使用新版本的OpenAI客户端
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        print("🔄 正在测试API连接...")
        
        # 测试API调用
        response = client.chat.completions.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "请回复'测试成功'"}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ API测试成功！")
        print(f"📝 响应：{result}")
        
        if response.usage:
            print(f"📊 Token使用：{response.usage.total_tokens} tokens")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        return False

if __name__ == "__main__":
    success = simple_test()
    
    if success:
        print("\n🎉 恭喜！API密钥工作正常！")
        print("现在可以继续下一步了。")
    else:
        print("\n❌ 测试失败，请检查网络连接")
    
    print("\n按Enter键退出...")
    input()

