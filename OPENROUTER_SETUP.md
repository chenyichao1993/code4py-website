# OpenRouter.ai API密钥设置指南

## 🌟 为什么选择OpenRouter？

[OpenRouter.ai](https://openrouter.ai/) 是一个统一的AI模型接口平台，提供以下优势：

- **更优惠的价格** - 比直接使用OpenAI便宜
- **更好的可用性** - 分布式基础设施，高可用性
- **统一接口** - 一个API访问多种模型
- **无需订阅** - 按使用量付费
- **OpenAI兼容** - 直接使用OpenAI SDK

## 🔑 获取OpenRouter API密钥详细步骤

### 第一步：注册OpenRouter账号

1. **访问OpenRouter官网**
   ```
   https://openrouter.ai/
   ```

2. **选择注册方式**
   - 点击 "Sign up" 按钮
   - 选择注册方式：
     - Google账号登录
     - GitHub账号登录
     - MetaMask钱包登录
     - 邮箱注册

3. **完善账号信息**
   - 设置用户名
   - 验证邮箱（如果使用邮箱注册）

### 第二步：购买Credits

1. **进入Credits页面**
   - 登录后，点击左侧菜单 "Settings" → "Credits"
   - 或者直接访问：https://openrouter.ai/settings/credits

2. **购买Credits**
   - 点击 "Add Credits" 按钮
   - 选择购买金额（建议从$10-20开始）
   - 选择支付方式：
     - 信用卡支付
     - 加密货币支付（开启"Use crypto"开关）
   - 确认购买

3. **设置自动充值（可选）**
   - 开启 "Auto Top-Up" 功能
   - 设置充值阈值（如余额低于$5时自动充值$20）

### 第三步：创建API密钥

1. **进入API Keys页面**
   - 点击左侧菜单 "Settings" → "API Keys"
   - 或者访问：https://openrouter.ai/settings/keys

2. **创建新密钥**
   - 点击 "Create Key" 按钮
   - 输入密钥名称（如：Code4Py-API-Key）
   - 选择权限范围（建议选择 "All"）
   - 点击创建

3. **保存密钥**
   - ⚠️ **重要**：密钥只显示一次，请立即复制保存
   - 格式：`sk-or-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 第四步：配置环境变量

1. **创建.env文件**
   在项目根目录创建 `.env` 文件：

   ```bash
   # OpenRouter Configuration
   OPENROUTER_API_KEY=sk-or-your-actual-api-key-here
   OPENROUTER_API_BASE=https://openrouter.ai/api/v1
   
   # 或者使用OpenAI API（二选一）
   # OPENAI_API_KEY=sk-your-openai-api-key-here
   
   # Database Configuration
   DATABASE_URL=postgresql://username:password@localhost:5432/code4py_db
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_PASSWORD=your_redis_password
   
   # JWT Configuration
   SECRET_KEY=your_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # Environment
   ENVIRONMENT=development
   ```

2. **替换API密钥**
   - 将 `sk-or-your-actual-api-key-here` 替换为你的实际API密钥
   - 确保密钥以 `sk-or-` 开头

### 第五步：测试API密钥

1. **安装依赖**
   ```bash
   pip install openai python-dotenv
   ```

2. **运行测试脚本**
   ```bash
   # 快速测试
   python quick_test_openrouter.py
   
   # 完整测试
   python test_openrouter_api.py
   ```

3. **检查输出**
   - 如果看到 "✅ OpenRouter API测试成功！" 说明配置正确
   - 如果看到错误信息，请检查API密钥和网络连接

## 💰 OpenRouter定价优势

### 价格对比（2024年）
| 模型 | OpenAI直接价格 | OpenRouter价格 | 节省 |
|------|----------------|----------------|------|
| GPT-3.5-turbo | $0.0015/1K tokens | $0.0005/1K tokens | 67% |
| GPT-4 | $0.03/1K tokens | $0.02/1K tokens | 33% |
| Claude-3.5-Sonnet | $0.003/1K tokens | $0.002/1K tokens | 33% |

### 预估成本
- 简单代码生成：$0.005-0.02/次
- 复杂代码生成：$0.02-0.10/次
- 月度预估：$5-50（取决于使用量）

## 🔧 代码集成

### 后端代码已更新
我已经更新了后端代码以支持OpenRouter：

```python
# 自动检测使用OpenRouter还是OpenAI
openai.api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")

# 使用正确的模型名称格式
model_name = "openai/gpt-3.5-turbo" if os.getenv("OPENROUTER_API_KEY") else "gpt-3.5-turbo"
```

### 支持的模型
OpenRouter支持多种模型，包括：
- `openai/gpt-3.5-turbo`
- `openai/gpt-4`
- `anthropic/claude-3.5-sonnet`
- `google/gemini-pro`
- 等等...

## 🔒 安全注意事项

### 1. 保护API密钥
- ❌ **不要**将API密钥提交到Git仓库
- ❌ **不要**在代码中硬编码API密钥
- ✅ **使用**环境变量存储API密钥
- ✅ **定期**轮换API密钥

### 2. 设置使用限制
- 设置月度使用限额
- 监控API使用情况
- 设置异常使用告警

### 3. 密钥管理
- 为不同环境使用不同密钥
- 定期检查密钥权限
- 及时删除不需要的密钥

## 🚨 常见问题

### Q1: 提示"Authentication failed"
**解决方案**：
- 检查API密钥是否正确
- 确认密钥以 `sk-or-` 开头
- 检查环境变量是否正确设置

### Q2: 提示"Insufficient quota"
**解决方案**：
- 检查账户余额
- 购买更多credits
- 检查使用限制设置

### Q3: 提示"Rate limit exceeded"
**解决方案**：
- 等待一段时间后重试
- 检查API使用频率
- 考虑升级到付费计划

### Q4: 模型名称错误
**解决方案**：
- 使用正确的模型名称格式：`provider/model`
- 例如：`openai/gpt-3.5-turbo`
- 查看OpenRouter支持的模型列表

## 📊 监控使用情况

### 查看使用统计
1. 登录OpenRouter
2. 进入 "Settings" → "Credits"
3. 点击 "View Usage" 查看详细使用情况

### 设置告警
- 设置余额告警
- 监控异常使用
- 定期检查费用

## ✅ 检查清单

完成以下步骤后，请确认：
- [ ] OpenRouter账号已注册
- [ ] Credits已购买
- [ ] API密钥已创建
- [ ] 环境变量已配置
- [ ] API测试通过
- [ ] 使用限制已设置

## 📞 技术支持

如果遇到问题：
1. 查看OpenRouter官方文档：https://openrouter.ai/docs
2. 联系OpenRouter支持：通过Discord或GitHub
3. 项目技术支持：motionjoy93@gmail.com

完成这些步骤后，您就可以进行下一步：部署后端服务了！

