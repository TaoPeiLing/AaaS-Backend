# 智能体服务平台 Makefile
# 提供常用的开发和部署命令

.PHONY: help install dev test lint format clean docker-build docker-run docker-stop

# 默认目标
help:
	@echo "智能体服务平台 - 可用命令:"
	@echo "  install     - 安装依赖"
	@echo "  dev         - 启动开发服务器"
	@echo "  test        - 运行测试"
	@echo "  lint        - 代码检查"
	@echo "  format      - 代码格式化"
	@echo "  clean       - 清理临时文件"
	@echo "  docker-build - 构建Docker镜像"
	@echo "  docker-run  - 运行Docker容器"
	@echo "  docker-stop - 停止Docker容器"

# 安装依赖
install:
	@echo "安装依赖..."
	uv venv
	uv pip install -r requirements.txt

# 启动开发服务器
dev:
	@echo "启动开发服务器..."
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 运行测试
test:
	@echo "运行测试..."
	uv run pytest

# 代码检查
lint:
	@echo "代码检查..."
	uv run mypy app/
	uv run black --check app/
	uv run isort --check-only app/

# 代码格式化
format:
	@echo "代码格式化..."
	uv run black app/
	uv run isort app/

# 清理临时文件
clean:
	@echo "清理临时文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -rf .coverage htmlcov/

# Docker相关命令
docker-build:
	@echo "构建Docker镜像..."
	docker build -t aaas-backend .

docker-run:
	@echo "运行Docker容器..."
	docker-compose up -d

docker-stop:
	@echo "停止Docker容器..."
	docker-compose down