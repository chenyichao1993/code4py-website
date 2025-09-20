# Code4Py - AI Python Code Generator

一个强大的AI驱动的Python代码生成器，可以将自然语言描述转换为生产就绪的Python代码。

## ✨ 功能特性

- 🤖 **AI代码生成** - 使用OpenAI GPT将自然语言转换为Python代码
- 🔄 **代码转换** - 支持多种编程语言到Python的转换
- 🧐 **代码解释** - 智能分析和解释Python代码
- 🐛 **代码调试** - 自动检测和修复代码问题
- 👤 **用户管理** - 支持用户注册、登录和订阅管理
- 🌍 **全球访问** - 通过Cloudflare CDN实现全球快速访问

## 🏗️ 技术架构

### 前端
- **HTML/CSS/JavaScript** - 响应式用户界面
- **Tailwind CSS** - 现代化样式设计
- **Vercel** - 静态网站托管

### 后端
- **FastAPI** - 高性能Python Web框架
- **OpenAI API** - AI代码生成
- **PostgreSQL** - 用户数据存储
- **Redis** - 缓存和会话管理
- **Railway** - 后端服务部署

### 基础设施
- **Cloudflare** - CDN和安全防护
- **GitHub Actions** - CI/CD自动化
- **Docker** - 容器化部署

## 🚀 快速开始

### 本地开发

1. **克隆仓库**
```bash
git clone https://github.com/yourusername/code4py.git
cd code4py
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，添加你的API密钥
```

4. **启动后端服务**
```bash
uvicorn app.main:app --reload
```

5. **打开前端**
```bash
# 直接在浏览器中打开 index.html
open index.html
```

### 生产部署

详细的部署指南请参考 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

## 📖 API 文档

### 代码生成
```http
POST /api/generate
Content-Type: application/json

{
  "prompt": "创建一个计算斐波那契数列的函数",
  "language": "python"
}
```

### 代码转换
```http
POST /api/convert
Content-Type: application/json

{
  "code": "console.log('Hello World');",
  "from_language": "javascript",
  "to_language": "python"
}
```

### 代码解释
```http
POST /api/explain
Content-Type: application/json

{
  "code": "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
  "language": "python"
}
```

## 🔧 配置

### 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API密钥 | 必需 |
| `DATABASE_URL` | PostgreSQL数据库连接 | 必需 |
| `REDIS_HOST` | Redis主机地址 | localhost |
| `REDIS_PORT` | Redis端口 | 6379 |
| `SECRET_KEY` | JWT密钥 | 必需 |
| `ENVIRONMENT` | 环境类型 | development |

## 🧪 测试

运行测试套件：
```bash
pytest tests/ -v
```

## 📊 监控

- **健康检查**: `GET /health`
- **API状态**: `GET /`
- **用户统计**: 通过数据库查询

## 🔒 安全

- JWT认证
- CORS策略
- 速率限制
- 输入验证
- SQL注入防护

## 💰 定价

### 免费版
- 每月20次代码生成
- 基础功能
- 社区支持

### 专业版 ($9.99/月)
- 无限代码生成
- 高级功能
- 优先支持
- API访问

### 企业版 ($99.99/月)
- 所有功能
- 私有部署
- 定制支持
- SLA保证

## 🤝 贡献

我们欢迎贡献！请查看 [CONTRIBUTING.md](./CONTRIBUTING.md) 了解详情。

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](./LICENSE) 文件了解详情。

## 📞 联系我们

- 网站: [code4py.com](https://code4py.com)
- 邮箱: motionjoy93@gmail.com
- GitHub: [项目仓库](https://github.com/yourusername/code4py)

## 🙏 致谢

- [OpenAI](https://openai.com) - AI代码生成
- [FastAPI](https://fastapi.tiangolo.com) - Web框架
- [Vercel](https://vercel.com) - 前端托管
- [Railway](https://railway.app) - 后端托管
- [Cloudflare](https://cloudflare.com) - CDN和安全

---

⭐ 如果这个项目对你有帮助，请给我们一个星标！


