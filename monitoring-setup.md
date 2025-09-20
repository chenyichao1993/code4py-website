# 监控和日志配置指南

## 📊 监控架构

```
用户请求 → Cloudflare → Vercel/Railway → 应用日志 → 监控系统
                ↓              ↓
            CDN分析        应用性能监控
                ↓              ↓
           安全事件        错误追踪
```

## 🔧 监控工具配置

### 1. Railway 内置监控

#### 应用监控
- **CPU使用率**: 实时监控
- **内存使用**: 实时监控  
- **网络流量**: 实时监控
- **响应时间**: 平均响应时间
- **错误率**: 4xx/5xx 错误统计

#### 日志管理
```bash
# 查看实时日志
railway logs --follow

# 查看错误日志
railway logs --filter="error"

# 导出日志
railway logs --export logs.json
```

### 2. Vercel 分析

#### Web Analytics
- 页面访问量
- 用户会话
- 跳出率
- 页面加载时间

#### 性能监控
- Core Web Vitals
- 首次内容绘制 (FCP)
- 最大内容绘制 (LCP)
- 累积布局偏移 (CLS)

### 3. Cloudflare 分析

#### 流量分析
- 请求量统计
- 带宽使用
- 缓存命中率
- 地理位置分布

#### 安全分析
- DDoS 攻击检测
- 恶意请求拦截
- Bot 流量分析
- 威胁情报

## 📈 自定义监控

### 1. 应用性能监控 (APM)

#### 后端监控
```python
# app/monitoring.py
import time
import logging
from functools import wraps
from fastapi import Request, Response

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def monitor_performance(func):
    """性能监控装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {str(e)}")
            raise
    return wrapper

def log_request(request: Request, response: Response):
    """记录请求日志"""
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"IP: {request.client.host}"
    )
```

#### 数据库监控
```python
# app/database_monitoring.py
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time
import logging

logger = logging.getLogger(__name__)

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    logger.info(f"Query executed in {total:.2f}s: {statement[:100]}...")
```

### 2. 错误追踪

#### Sentry 集成
```python
# requirements.txt 添加
sentry-sdk[fastapi]==1.38.0

# app/main.py 添加
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[
        FastApiIntegration(auto_enabling_instrumentations=True),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=1.0,
    environment="production",
)
```

#### 自定义错误处理
```python
# app/error_handlers.py
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)} - {request.url}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

### 3. 业务指标监控

#### 用户行为追踪
```python
# app/analytics.py
import json
from datetime import datetime
from typing import Dict, Any

class AnalyticsTracker:
    def __init__(self):
        self.events = []
    
    def track_event(self, event_type: str, properties: Dict[str, Any]):
        """追踪用户事件"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "properties": properties
        }
        self.events.append(event)
        logger.info(f"Event tracked: {event_type}")
    
    def track_code_generation(self, user_id: str, prompt_length: int, language: str):
        """追踪代码生成事件"""
        self.track_event("code_generated", {
            "user_id": user_id,
            "prompt_length": prompt_length,
            "language": language
        })
    
    def track_user_registration(self, user_id: str, email: str):
        """追踪用户注册事件"""
        self.track_event("user_registered", {
            "user_id": user_id,
            "email": email
        })

# 全局实例
analytics = AnalyticsTracker()
```

## 📊 监控仪表板

### 1. Railway 仪表板

#### 关键指标
- **响应时间**: < 500ms
- **错误率**: < 1%
- **CPU使用率**: < 80%
- **内存使用率**: < 80%

#### 告警设置
```yaml
# railway.yml
alerts:
  - name: "High CPU Usage"
    condition: "cpu_percent > 80"
    duration: "5m"
    action: "notify"
  
  - name: "High Error Rate"
    condition: "error_rate > 5%"
    duration: "2m"
    action: "notify"
```

### 2. 自定义仪表板

#### Grafana 配置 (可选)
```json
{
  "dashboard": {
    "title": "Code4Py Monitoring",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "avg(response_time)",
            "legendFormat": "Average Response Time"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "singlestat",
        "targets": [
          {
            "expr": "rate(errors_total[5m])",
            "legendFormat": "Error Rate"
          }
        ]
      }
    ]
  }
}
```

## 🚨 告警配置

### 1. 邮件告警

#### SMTP 配置
```python
# app/notifications.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailNotifier:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL")
    
    def send_alert(self, subject: str, message: str, to_emails: list):
        """发送告警邮件"""
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = ", ".join(to_emails)
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'plain'))
        
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.starttls()
        server.login(self.username, self.password)
        server.send_message(msg)
        server.quit()
```

### 2. Slack 告警

#### Slack Webhook
```python
# app/slack_notifier.py
import requests
import json

class SlackNotifier:
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    def send_alert(self, message: str, channel: str = "#alerts"):
        """发送 Slack 告警"""
        payload = {
            "channel": channel,
            "text": message,
            "username": "Code4Py Monitor",
            "icon_emoji": ":warning:"
        }
        
        response = requests.post(
            self.webhook_url,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.status_code == 200
```

## 📋 监控检查清单

### 部署前检查
- [ ] 日志配置正确
- [ ] 监控工具集成
- [ ] 告警规则设置
- [ ] 性能基线建立
- [ ] 错误追踪配置

### 部署后验证
- [ ] 日志正常输出
- [ ] 监控数据收集
- [ ] 告警功能测试
- [ ] 性能指标正常
- [ ] 错误追踪工作

### 日常维护
- [ ] 日志文件清理
- [ ] 监控数据备份
- [ ] 告警规则优化
- [ ] 性能趋势分析
- [ ] 错误模式识别

## 🔍 故障排除

### 常见问题

#### 1. 日志不输出
- 检查日志级别设置
- 验证文件权限
- 确认磁盘空间

#### 2. 监控数据缺失
- 检查网络连接
- 验证API密钥
- 确认服务状态

#### 3. 告警不触发
- 检查阈值设置
- 验证通知配置
- 测试告警功能

## 📞 技术支持

监控相关问题请联系：
- 技术支持: motionjoy93@gmail.com
- 监控工具文档: 各工具官方文档
- GitHub Issues: 项目仓库


