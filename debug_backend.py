#!/usr/bin/env python3
"""
调试后端500错误
"""

import requests
import json
import traceback

def debug_backend():
    print("🔍 调试后端500错误")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # 测试代码生成API
    print("测试代码生成API...")
    try:
        payload = {
            "prompt": "创建一个简单的hello world函数",
            "language": "python"
        }
        
        print(f"请求URL: {base_url}/api/generate")
        print(f"请求数据: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{base_url}/api/generate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 成功! 响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 错误响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误: 无法连接到服务器")
        print("请确保后端服务正在运行")
    except requests.exceptions.Timeout:
        print("❌ 超时错误: 请求超时")
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_backend()

