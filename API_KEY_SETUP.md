# OpenAI API密钥设置指南

## 🔑 获取API密钥详细步骤

### 第一步：注册OpenAI账号

1. **访问OpenAI官网**
   ```
   https://platform.openai.com
   ```

2. **点击注册**
   - 点击右上角 "Sign up"
   - 输入邮箱地址
   - 设置密码（至少8位，包含大小写字母和数字）
   - 验证邮箱

3. **完善信息**
   - 填写姓名
   - 选择国家/地区
   - 验证手机号码

### 第二步：设置付费方式

⚠️ **重要**：OpenAI API是付费服务，需要绑定信用卡

1. **进入付费设置**
   - 登录后点击右上角头像
   - 选择 "Billing" 或 "Usage"
   - 点击 "Add payment method"

2. **添加信用卡**
   - 输入信用卡信息
   - 填写账单地址
   - 确认支付方式

3. **设置使用限制**
   - 建议设置月度使用限额（如$20-50）
   - 避免意外高额费用

### 第三步：创建API密钥

1. **进入API密钥页面**
   ```
   https://platform.openai.com/api-keys
   ```

2. **创建新密钥**
   - 点击 "Create new secret key"
   - 输入密钥名称（如：Code4Py-API-Key）
   - 选择权限范围（建议选择 "All"）

3. **保存密钥**
   - ⚠️ **重要**：密钥只显示一次，请立即复制保存
   - 格式：`sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 第四步：配置环境变量

1. **创建.env文件**
   在项目根目录创建 `.env` 文件：

   ```bash
   # OpenAI Configuration
   OPENAI_API_KEY=sk-your-actual-api-key-here
   
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
   - 将 `sk-your-actual-api-key-here` 替换为你的实际API密钥
   - 确保密钥以 `sk-` 开头

### 第五步：测试API密钥

1. **安装依赖**
   ```bash
   pip install openai python-dotenv
   ```

2. **运行测试脚本**
   ```bash
   python test_openai_api.py
   ```

3. **检查输出**
   - 如果看到 "✅ API测试成功！" 说明配置正确
   - 如果看到错误信息，请检查API密钥和网络连接

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

## 💰 费用说明

### OpenAI API定价（2024年）
- **GPT-3.5-turbo**: $0.0015/1K tokens (输入), $0.002/1K tokens (输出)
- **GPT-4**: $0.03/1K tokens (输入), $0.06/1K tokens (输出)

### 预估成本
- 简单代码生成：$0.01-0.05/次
- 复杂代码生成：$0.05-0.20/次
- 月度预估：$10-100（取决于使用量）

## 🚨 常见问题

### Q1: 提示"Authentication failed"
**解决方案**：
- 检查API密钥是否正确
- 确认密钥以 `sk-` 开头
- 检查环境变量是否正确设置

### Q2: 提示"Insufficient quota"
**解决方案**：
- 检查账户余额
- 添加付费方式
- 检查使用限制设置

### Q3: 提示"Rate limit exceeded"
**解决方案**：
- 等待一段时间后重试
- 检查API使用频率
- 考虑升级到付费计划

### Q4: 网络连接问题
**解决方案**：
- 检查网络连接
- 确认防火墙设置
- 尝试使用VPN

## 📞 技术支持

如果遇到问题：
1. 查看OpenAI官方文档：https://platform.openai.com/docs
2. 联系OpenAI支持：https://help.openai.com
3. 项目技术支持：motionjoy93@gmail.com

## ✅ 检查清单

完成以下步骤后，请确认：
- [ ] OpenAI账号已注册
- [ ] 付费方式已设置
- [ ] API密钥已创建
- [ ] 环境变量已配置
- [ ] API测试通过
- [ ] 使用限制已设置

完成这些步骤后，您就可以进行下一步：部署后端服务了！


