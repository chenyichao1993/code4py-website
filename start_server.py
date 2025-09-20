#!/usr/bin/env python3
"""
启动后端服务
"""

import uvicorn
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

if __name__ == "__main__":
    print("🚀 启动Code4Py后端服务...")
    print("=" * 50)
    
    # 检查环境变量
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        print(f"✅ API密钥已加载: {api_key[:20]}...")
    else:
        print("❌ 警告：未找到API密钥")
    
    # 启动服务
    try:
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ 启动失败：{e}")
        print("请检查端口8000是否被占用")

