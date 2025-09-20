#!/usr/bin/env python3
"""
测试API连接
"""

import requests
import json

def test_api():
    print("🧪 测试API连接")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # 测试1: 根路径
    print("1. 测试根路径...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 测试2: 健康检查
    print("\n2. 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 测试3: API生成
    print("\n3. 测试代码生成API...")
    try:
        payload = {
            "prompt": "创建一个简单的hello world函数",
            "language": "python"
        }
        response = requests.post(
            f"{base_url}/api/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 成功! 生成代码长度: {len(data.get('code', ''))}")
            print(f"   代码预览: {data.get('code', '')[:100]}...")
        else:
            print(f"   ❌ 错误: {response.text}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 测试4: CORS
    print("\n4. 测试CORS...")
    try:
        response = requests.options(
            f"{base_url}/api/generate",
            headers={
                "Origin": "file://",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        print(f"   状态码: {response.status_code}")
        print(f"   CORS头: {dict(response.headers)}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")

if __name__ == "__main__":
    test_api()

