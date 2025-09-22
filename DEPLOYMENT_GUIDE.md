# Code4Py 部署指南

## 概述

Code4Py是一个AI驱动的Python代码生成器，使用Replicate API和Render部署。

## 技术栈

- **前端**: HTML/CSS/JavaScript + Tailwind CSS (Vercel部署)
- **后端**: FastAPI + Python (Render部署)
- **AI服务**: Replicate API (Llama-2模型)
- **数据库**: PostgreSQL + Redis (可选，用于缓存和限流)

## 部署步骤

### 1. 前端部署 (Vercel)

1. 将项目推送到GitHub仓库
2. 在Vercel中导入项目
3. 选择前端目录，Vercel会自动检测为静态网站
4. 部署完成后，记录前端URL

### 2. 后端部署 (Render)

1. 在Render中创建新的Web Service
2. 连接GitHub仓库
3. 配置以下设置：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Python Version**: 3.9+

### 3. 环境变量配置

在Render的环境变量中设置：

```bash
# Replicate API (必需)
REPLICATE_API_TOKEN=r8_your-actual-replicate-token

# 数据库 (可选，用于用户管理)
DATABASE_URL=postgresql://username:password@host:port/database

# Redis (可选，用于缓存和限流)
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# 安全配置
SECRET_KEY=your-super-secret-key-here

# 应用配置
APP_NAME=Code4Py
APP_VERSION=1.0.0
ENVIRONMENT=production
```

### 4. 获取Replicate API Token

1. 访问 [Replicate](https://replicate.com)
2. 注册账户并登录
3. 在账户设置中找到API Token
4. 复制token并设置到环境变量中

### 5. 更新前端API地址

在 `index.html` 中更新API地址：

```javascript
const API_BASE_URL = 'https://your-render-app-name.onrender.com';
```

### 6. 测试部署

1. 访问前端网站
2. 尝试生成代码
3. 检查浏览器控制台是否有错误
4. 检查Render日志是否有错误

## 故障排除

### 常见问题

1. **"Code generation failed"错误**
   - 检查Replicate API token是否正确
   - 检查Render日志中的错误信息
   - 确认Replicate账户有足够余额

2. **前端无法连接后端**
   - 检查API_BASE_URL是否正确
   - 检查CORS设置
   - 确认Render服务正在运行

3. **Redis连接错误**
   - Redis是可选的，错误不会影响基本功能
   - 如需使用Redis，请配置正确的连接信息

### 日志查看

在Render控制台中查看日志：
1. 进入Web Service
2. 点击"Logs"标签
3. 查看实时日志

### 性能优化

1. **启用Redis缓存** (可选)
   - 减少API调用次数
   - 提高响应速度

2. **数据库优化** (可选)
   - 用于用户管理和使用统计
   - 提高数据持久性

## 监控和维护

### 健康检查

访问 `https://your-app.onrender.com/health` 检查服务状态

### 使用统计

- 免费用户每日限制10次生成
- 可通过Redis或数据库跟踪使用情况

### 更新部署

1. 推送代码到GitHub
2. Render会自动重新部署
3. 检查部署日志确认成功

## 安全考虑

1. **API Token安全**
   - 不要在代码中硬编码API token
   - 定期轮换API token

2. **CORS配置**
   - 在生产环境中限制允许的域名
   - 避免使用通配符 `*`

3. **速率限制**
   - 已实现每日使用限制
   - 可添加更严格的速率限制

## 成本估算

### Render (免费层)
- 每月750小时免费
- 适合开发和测试

### Replicate
- 按使用量计费
- Llama-2-70B: ~$0.00065/1K tokens
- 预估每月成本: $5-20 (取决于使用量)

### Vercel
- 免费层足够静态网站使用

## 支持

如有问题，请检查：
1. Render部署日志
2. 浏览器控制台错误
3. Replicate API状态
4. 环境变量配置

---

**注意**: 确保在生产环境中设置正确的环境变量，特别是API token和安全密钥。
