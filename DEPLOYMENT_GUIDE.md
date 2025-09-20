# Code4Py 部署指南

## 🚀 整体部署方案

### 架构概览
```
用户 → Cloudflare CDN → Vercel (前端) → Railway (后端) → OpenAI API
                    ↓
                PostgreSQL + Redis
```

## 📋 部署步骤

### 1. 后端部署 (Railway)

#### 1.1 准备环境变量
创建 `.env` 文件：
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration  
DATABASE_URL=postgresql://username:password@host:port/database
REDIS_HOST=your_redis_host
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# JWT Configuration
SECRET_KEY=your_very_secure_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=production
```

#### 1.2 部署到 Railway
1. 访问 [Railway.app](https://railway.app)
2. 连接 GitHub 仓库
3. 选择后端项目文件夹
4. Railway 会自动检测到 `railway.json` 配置
5. 设置环境变量
6. 部署完成后获取后端 URL

### 2. 前端部署 (Vercel)

#### 2.1 更新 API 地址
在 `index.html` 中更新：
```javascript
const API_BASE_URL = 'https://your-actual-backend-url.railway.app';
```

#### 2.2 部署到 Vercel
1. 访问 [Vercel.com](https://vercel.com)
2. 连接 GitHub 仓库
3. 选择前端项目文件夹
4. Vercel 会自动检测到 `vercel.json` 配置
5. 部署完成后获取前端 URL

### 3. 域名配置 (Cloudflare)

#### 3.1 添加域名到 Cloudflare
1. 登录 [Cloudflare](https://cloudflare.com)
2. 添加 `code4py.com` 域名
3. 更新 DNS 记录：
   - A 记录: `@` → Vercel IP
   - CNAME: `www` → `code4py.com`

#### 3.2 配置 CDN
1. 启用 Cloudflare CDN
2. 配置缓存规则
3. 启用 SSL/TLS
4. 配置安全规则

### 4. 数据库设置

#### 4.1 PostgreSQL (Railway)
1. 在 Railway 中添加 PostgreSQL 服务
2. 获取连接字符串
3. 更新环境变量 `DATABASE_URL`

#### 4.2 Redis (Railway)
1. 在 Railway 中添加 Redis 服务
2. 获取连接信息
3. 更新环境变量 `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`

## 🔧 配置详情

### Railway 配置
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Vercel 配置
```json
{
  "version": 2,
  "builds": [
    {
      "src": "index.html",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

## 📊 监控和日志

### 1. Railway 监控
- 自动监控应用健康状态
- 查看日志和性能指标
- 设置告警通知

### 2. Vercel 分析
- 访问量统计
- 性能监控
- 错误追踪

### 3. Cloudflare 分析
- CDN 性能
- 安全事件
- 流量分析

## 🔒 安全配置

### 1. API 安全
- 实现 JWT 认证
- 设置 CORS 策略
- 添加速率限制
- 输入验证和清理

### 2. 数据库安全
- 使用连接池
- 定期备份
- 访问控制

### 3. CDN 安全
- DDoS 防护
- WAF 规则
- SSL/TLS 加密

## 💰 成本估算

### 免费额度
- **Vercel**: 100GB 带宽/月
- **Railway**: $5 免费额度
- **Cloudflare**: 免费 CDN
- **OpenAI**: 按使用量付费

### 预估月成本
- 小规模使用: $10-20
- 中等规模: $50-100
- 大规模: $200+

## 🚨 故障排除

### 常见问题
1. **API 连接失败**
   - 检查 CORS 配置
   - 验证 API URL
   - 检查网络连接

2. **数据库连接问题**
   - 验证连接字符串
   - 检查防火墙设置
   - 确认服务状态

3. **域名解析问题**
   - 检查 DNS 记录
   - 等待 DNS 传播
   - 验证 SSL 证书

## 📈 性能优化

### 1. 前端优化
- 启用 Gzip 压缩
- 使用 CDN 缓存
- 优化图片和资源

### 2. 后端优化
- 数据库索引优化
- Redis 缓存
- API 响应压缩

### 3. CDN 优化
- 静态资源缓存
- 边缘计算
- 智能路由

## 🔄 持续部署

### GitHub Actions
```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.ORG_ID }}
          vercel-project-id: ${{ secrets.PROJECT_ID }}
```

## 📞 技术支持

如有问题，请联系：
- 邮箱: motionjoy93@gmail.com
- GitHub Issues: 项目仓库
- 文档: 本部署指南


