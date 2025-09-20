# Cloudflare 配置指南

## 🌐 域名配置步骤

### 1. 添加域名到 Cloudflare

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com)
2. 点击 "Add a Site"
3. 输入 `code4py.com`
4. 选择免费计划
5. 等待 DNS 扫描完成

### 2. DNS 记录配置

#### 主要记录
```
类型: A
名称: @
IPv4 地址: Vercel 提供的 IP 地址
代理状态: 已代理 (橙色云朵)
```

```
类型: CNAME
名称: www
目标: code4py.com
代理状态: 已代理 (橙色云朵)
```

#### API 子域名 (可选)
```
类型: CNAME
名称: api
目标: your-backend-url.railway.app
代理状态: 已代理 (橙色云朵)
```

### 3. SSL/TLS 配置

1. 进入 "SSL/TLS" 页面
2. 加密模式选择: "Full (strict)"
3. 启用 "Always Use HTTPS"
4. 启用 "HTTP Strict Transport Security (HSTS)"

### 4. 缓存配置

#### 页面规则
```
URL: code4py.com/*
设置:
- 缓存级别: 标准
- 边缘缓存 TTL: 1 个月
- 浏览器缓存 TTL: 1 个月
```

```
URL: code4py.com/api/*
设置:
- 缓存级别: 绕过
- 边缘缓存 TTL: 不设置
```

### 5. 安全配置

#### WAF 规则
```javascript
// 阻止恶意请求
(http.request.uri.path contains "/admin" or 
 http.request.uri.path contains "/wp-admin" or
 http.request.uri.path contains "/.env")
```

#### 速率限制
```
规则名称: API 速率限制
匹配: code4py.com/api/*
限制: 每分钟 100 个请求
操作: 阻止
```

### 6. 性能优化

#### 自动优化
- ✅ 自动压缩
- ✅ Brotli 压缩
- ✅ Rocket Loader
- ✅ Mirage

#### 缓存设置
```
缓存级别: 标准
边缘缓存 TTL: 1 个月
浏览器缓存 TTL: 1 个月
```

### 7. 分析配置

#### Web Analytics
- 启用 "Web Analytics"
- 启用 "Bot Analytics"
- 启用 "Security Analytics"

#### 自定义事件
```javascript
// 跟踪代码生成事件
gtag('event', 'code_generated', {
  'event_category': 'engagement',
  'event_label': 'python_code'
});
```

## 🔧 高级配置

### 1. Workers (可选)

创建边缘计算函数：
```javascript
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  // 处理 API 请求
  if (request.url.includes('/api/')) {
    return fetch(request)
  }
  
  // 处理静态资源
  return fetch(request)
}
```

### 2. 自定义错误页面

创建 404 页面：
```html
<!DOCTYPE html>
<html>
<head>
    <title>页面未找到 - Code4Py</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    <h1>404 - 页面未找到</h1>
    <p>抱歉，您访问的页面不存在。</p>
    <a href="/">返回首页</a>
</body>
</html>
```

### 3. 重定向规则

```
源 URL: code4py.com/*
目标 URL: https://code4py.com/$1
状态码: 301
```

## 📊 监控和告警

### 1. 告警设置

#### 高流量告警
- 条件: 每分钟请求数 > 1000
- 通知: 邮件 + Slack

#### 错误率告警
- 条件: 5xx 错误率 > 5%
- 通知: 邮件 + Slack

#### 安全事件告警
- 条件: 安全事件 > 10/分钟
- 通知: 邮件 + Slack

### 2. 分析报告

#### 每日报告
- 访问量统计
- 性能指标
- 安全事件
- 错误分析

#### 每周报告
- 趋势分析
- 用户行为
- 优化建议

## 🚀 部署检查清单

### 部署前检查
- [ ] DNS 记录正确配置
- [ ] SSL 证书有效
- [ ] 缓存规则设置
- [ ] 安全规则配置
- [ ] 重定向规则测试
- [ ] 错误页面配置

### 部署后验证
- [ ] 网站正常访问
- [ ] HTTPS 强制重定向
- [ ] API 接口正常
- [ ] 缓存生效
- [ ] 安全防护激活
- [ ] 分析数据收集

## 🔍 故障排除

### 常见问题

#### 1. DNS 解析问题
- 检查 DNS 记录是否正确
- 等待 DNS 传播 (最多 24 小时)
- 使用 `nslookup` 验证

#### 2. SSL 证书问题
- 确保域名已添加到 Cloudflare
- 检查 SSL 模式设置
- 验证证书状态

#### 3. 缓存问题
- 清除 Cloudflare 缓存
- 检查页面规则设置
- 验证缓存头设置

#### 4. 性能问题
- 启用自动优化
- 检查压缩设置
- 优化图片和资源

## 📞 技术支持

如遇到问题，请联系：
- Cloudflare 支持: [support.cloudflare.com](https://support.cloudflare.com)
- 项目邮箱: motionjoy93@gmail.com
- GitHub Issues: 项目仓库


