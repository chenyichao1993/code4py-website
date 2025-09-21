# Debug功能配置说明

## 问题诊断

您的debug功能出错是因为缺少API密钥配置。错误信息显示 "User not found" (401错误)，这表明OpenRouter API无法验证您的身份。

## 解决方案

### 1. 获取OpenRouter API密钥

1. 访问 [OpenRouter.ai](https://openrouter.ai/)
2. 注册账户并登录
3. 在控制台中创建API密钥
4. 复制您的API密钥（格式：`sk-or-v1-...`）

### 2. 配置环境变量

#### 方法A：创建 .env 文件（推荐）

在项目根目录创建 `.env` 文件：

```bash
# OpenAI/OpenRouter API
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
OPENROUTER_API_BASE=https://openrouter.ai/api/v1

# 数据库连接（可选）
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# 应用配置
APP_NAME=Code4Py
APP_VERSION=1.0.0
ENVIRONMENT=development
```

#### 方法B：设置系统环境变量

**Windows:**
```cmd
set OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
set OPENROUTER_API_BASE=https://openrouter.ai/api/v1
```

**Linux/Mac:**
```bash
export OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
export OPENROUTER_API_BASE=https://openrouter.ai/api/v1
```

### 3. 重启应用

配置环境变量后，重启您的FastAPI应用：

```bash
python -m uvicorn app.main:app --reload
```

### 4. 测试debug功能

访问您的网站，选择 "🐛 Debug Code" 功能，输入以下测试代码：

```python
def divide(a, b):
    return a / b
```

如果配置正确，您应该看到详细的调试分析结果。

## 故障排除

### 常见错误及解决方案

1. **"User not found" (401错误)**
   - 检查API密钥是否正确
   - 确保API密钥有效且未过期

2. **"Rate limit exceeded" (429错误)**
   - 等待几分钟后重试
   - 检查您的API使用配额

3. **"Request timeout"**
   - 检查网络连接
   - 稍后重试

4. **环境变量未生效**
   - 确保重启了应用
   - 检查环境变量名称是否正确

## 其他功能

配置完成后，以下功能也应该正常工作：
- 🔧 Generate Code（生成代码）
- 🔄 Convert Code（代码转换）
- 📖 Explain Code（代码解释）
- 🐛 Debug Code（代码调试）

## 支持

如果仍有问题，请检查：
1. API密钥是否有效
2. 网络连接是否正常
3. 应用是否已重启
4. 环境变量是否正确设置

