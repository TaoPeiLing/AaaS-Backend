# 智能体服务平台

基于 LangChain v0.3 + LangGraph 构建的智能体服务平台，为小商家提供小红书爆款、朋友圈生成等智能体服务。

## 🌟 特性

- **多智能体支持**: 小红书爆款智能体、朋友圈生成智能体等
- **国产模型集成**: 支持百度文心一言、阿里通义千问、腾讯混元等
- **灵活架构**: 基于 LangGraph 的智能体工作流
- **高性能**: FastAPI + 异步处理，支持高并发
- **企业级**: 完善的日志、监控、异常处理系统
- **现代化工具**: 使用 uv 进行快速依赖管理
- **易部署**: Docker 容器化部署

## 🏗️ 技术架构

### 核心技术栈
- **后端框架**: FastAPI 0.104+
- **智能体框架**: LangChain 0.3 + LangGraph 0.2
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **模型集成**: 智谱AI GLM-4、百度文心一言、阿里通义千问
- **依赖管理**: uv (快速Python包管理器)
- **容器化**: Docker + Docker Compose

### 项目结构
```
app/
├── agents/          # 智能体实现
│   ├── core/        # 核心基类和接口
│   ├── factories/   # 智能体工厂
│   └── implementations/  # 具体智能体实现
├── api/             # API路由
├── core/            # 核心配置和工具
├── database/        # 数据库相关
├── models/          # 模型适配器
└── prompts/         # 提示词管理
```

## 🚀 快速开始

### 前置要求

- **Python**: 3.8+
- **uv**: 现代化的Python包管理器 (推荐)
- **Git**: 版本控制工具

### 1. 环境准备

```bash
# 安装 uv (如果尚未安装)
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 克隆项目
git clone https://github.com/TaoPeiLing/AaaS-Backend.git
cd AaaS-Backend

# 使用 uv 创建虚拟环境并安装依赖
uv venv
uv pip install -r requirements.txt
```

### 2. 配置环境

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑 .env 文件，配置API密钥
# 至少需要配置一个模型提供商的API密钥
```

### 3. 启动服务

```bash
# 推荐方式：使用 uv run 直接运行（自动使用虚拟环境）
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 使用 Docker Compose
docker-compose up -d
```

### 4. 访问服务

- **API文档**: http://localhost:8000/api/v1/docs
- **健康检查**: http://localhost:8000/health
- **根路径**: http://localhost:8000/

## 📖 API 使用指南

### 智能体管理

#### 获取智能体类型
```bash
curl -X GET "http://localhost:8000/api/v1/agents/types"
```

#### 小红书内容生成
```bash
curl -X POST "http://localhost:8000/api/v1/agents/xiaohongshu/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "护肤品",
    "style": "种草",
    "target_audience": "年轻女性",
    "keywords": ["平价", "好用", "学生党"],
    "length": "中等"
  }'
```

#### 朋友圈内容生成
```bash
curl -X POST "http://localhost:8000/api/v1/agents/wechat-moments/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "美食推荐",
    "main_content": "今天去了一家新开的川菜馆，味道很不错",
    "tone": "轻松",
    "include_emoji": true,
    "length": "适中"
  }'
```

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `ENVIRONMENT` | 运行环境 | `development` |
| `DATABASE_URL` | 数据库连接URL | `sqlite:///./agent_platform.db` |
| `ZHIPUAI_API_KEY` | 智谱AI API密钥 | - |
| `BAIDU_API_KEY` | 百度API密钥 | - |
| `DASHSCOPE_API_KEY` | 阿里API密钥 | - |

### 模型提供商配置

支持的模型提供商：

1. **智谱AI GLM-4**
   - 需要配置: `ZHIPUAI_API_KEY`
   - 支持模型: `glm-4`, `glm-4v`

2. **百度文心一言**
   - 需要配置: `BAIDU_API_KEY`, `BAIDU_SECRET_KEY`
   - 支持模型: `ernie-3.5-turbo`, `ernie-4.0-turbo`

3. **阿里通义千问**
   - 需要配置: `DASHSCOPE_API_KEY`
   - 支持模型: `qwen-turbo`, `qwen-plus`, `qwen-max`

## 🏢 生产部署

### Docker 部署

```bash
# 构建镜像
docker build -t aaas-backend .

# 运行容器
docker run -d \
  --name aaas-backend \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e ZHIPUAI_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  aaas-backend
```

### Docker Compose 部署

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 🧪 开发指南

### 开发环境设置

```bash
# 使用 uv 进行开发环境设置
uv venv --python 3.11  # 指定Python版本创建虚拟环境
uv pip install -r requirements.txt

# 安装开发依赖
uv pip install pytest black isort mypy

# 使用 uv run 运行开发工具（自动使用虚拟环境）
uv run black app/      # 代码格式化
uv run isort app/      # 导入排序
uv run mypy app/       # 类型检查
uv run pytest         # 运行测试
```

### 添加新的智能体

1. 继承 `BaseAgent` 类
2. 实现必要的抽象方法
3. 在工厂中注册智能体类型
4. 添加对应的API接口

### 添加新的模型提供商

1. 继承 `ModelAdapter` 类
2. 实现API调用逻辑
3. 在工厂中注册适配器
4. 更新配置文件

## 🤝 贡献指南

1. Fork 项目
2. 克隆到本地并设置开发环境
3. 创建特性分支 (`git checkout -b feature/amazing-feature`)
4. 进行更改并确保代码质量
5. 提交更改 (`git commit -m 'Add amazing feature'`)
6. 推送到分支 (`git push origin feature/amazing-feature`)
7. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔄 更新日志

### v1.1.0 (2024-12-25) - LangChain 0.3 兼容性升级

#### 🔄 重大变更
- **LangGraph API 更新**: 替换废弃的 `END` 常量为 `"__end__"` 字符串
- **模型调用API升级**: 将 `agenerate` 方法替换为 `ainvoke`
- **流式调用优化**: 修复 `astream` 方法的参数传递方式

#### ✨ 新增功能
- **增强错误处理**: 添加完整的异常处理和结构化日志
- **Token统计改进**: 支持新的 `usage_metadata` 格式
- **兼容性测试**: 新增 LangChain 0.3 兼容性验证

#### 🔧 技术改进
- **依赖版本优化**: 更新 LangGraph 版本范围为 `>=0.2.20,<0.3.0`
- **类型注解增强**: 改进类型提示和代码质量
- **CI/CD集成**: 添加自动化兼容性检查

### v1.0.0 (2024-01-XX)
- 初始版本发布
- 支持小红书和朋友圈智能体
- 集成智谱AI GLM-4
- 完整的API接口和文档