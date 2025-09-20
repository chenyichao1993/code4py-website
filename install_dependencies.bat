@echo off
echo 🚀 正在安装Python依赖包...
echo.

echo 安装 python-dotenv...
pip install python-dotenv

echo 安装 fastapi...
pip install fastapi

echo 安装 uvicorn...
pip install uvicorn

echo 安装 openai...
pip install openai

echo 安装 redis...
pip install redis

echo 安装 sqlalchemy...
pip install sqlalchemy

echo 安装 pydantic...
pip install pydantic

echo 安装 python-multipart...
pip install python-multipart

echo.
echo ✅ 依赖安装完成！
echo.
echo 现在可以启动后端服务了：
echo uvicorn app.main:app --reload
echo.
pause

