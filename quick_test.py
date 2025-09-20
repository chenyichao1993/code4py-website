#!/usr/bin/env python3
"""
快速测试OpenAI API密钥
"""

import openai
import os

def quick_test():
    print("🚀 OpenAI API 快速测试")
    print("=" * 40)
    
    # 获取API密钥
    api_key = input("请输入您的OpenAI API密钥 (sk-开头): ").strip()
    
    if not api_key:
        print("❌ 错误：未输入API密钥")
        return False
    
    if not api_key.startswith("sk-"):
        print("❌ 错误：API密钥格式不正确，应该以'sk-'开头")
        return False
    
    # 设置OpenAI客户端
    openai.api_key = api_key
    
    try:
        print("🔄 正在测试API连接...")
        
        # 测试API调用
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
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
        
    except openai.error.AuthenticationError:
        print("❌ 认证失败：API密钥无效")
        return False
        
    except openai.error.RateLimitError:
        print("❌ 速率限制：请求过于频繁")
        return False
        
    except openai.error.InsufficientQuota:
        print("❌ 配额不足：账户余额不足")
        return False
        
    except Exception as e:
        print(f"❌ 错误：{str(e)}")
        return False

if __name__ == "__main__":
    success = quick_test()
    
    if success:
        print("\n🎉 恭喜！API密钥配置成功！")
        print("现在可以将API密钥添加到.env文件中：")
        print("OPENAI_API_KEY=你的API密钥")
    else:
        print("\n❌ API密钥测试失败，请检查配置")
    
    print("\n按Enter键退出...")
    input()


