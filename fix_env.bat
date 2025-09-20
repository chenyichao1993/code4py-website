@echo off
echo 🚀 正在修复.env文件...
echo.

echo 删除旧的.env文件...
del .env 2>nul

echo 创建新的.env文件...
python create_env.py

echo.
echo ✅ 修复完成！
echo.
echo 现在可以启动后端服务了：
echo uvicorn app.main:app --reload
echo.
pause

