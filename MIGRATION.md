# LangChain 0.3 升级迁移指南

## 📋 概述

本文档详细说明了从 LangChain 0.2.x 升级到 0.3.x 的迁移步骤和注意事项。

## 🔄 主要变更

### 1. LangGraph API 变更

#### 问题：END 常量废弃
```python
# ❌ 旧版本 (LangGraph < 0.2.20)
from langgraph.graph import StateGraph, END

workflow.add_edge("format_response", END)
workflow.add_conditional_edges(
    "agent",
    self._should_continue,
    {
        "continue": "tools",
        "end": END
    }
)
```

```python
# ✅ 新版本 (LangGraph >= 0.2.20)
from langgraph.graph import StateGraph

workflow.add_edge("format_response", "__end__")
workflow.add_conditional_edges(
    "agent",
    self._should_continue,
    {
        "continue": "tools",
        "end": "__end__"
    }
)
```

### 2. 模型调用 API 变更

#### 问题：agenerate 方法废弃
```python
# ❌ 旧版本
result = await self.langchain_model.agenerate([messages])
generation = result.generations[0][0]
content = generation.text
```

```python
# ✅ 新版本
result = await self.langchain_model.ainvoke(messages)
content = result.content
```

### 3. 流式调用优化

#### 问题：astream 参数传递
```python
# ❌ 旧版本
async for chunk in self.langchain_model.astream(messages, **kwargs):
    yield chunk.content
```

```python
# ✅ 新版本
async for chunk in self.langchain_model.astream(messages):
    if hasattr(chunk, 'content') and chunk.content:
        yield chunk.content
```

### 4. Token统计改进

#### 问题：usage_metadata 格式变更
```python
# ❌ 旧版本
if hasattr(result, 'llm_output') and result.llm_output:
    token_usage = result.llm_output.get('token_usage', {})
```

```python
# ✅ 新版本
if hasattr(result, 'usage_metadata') and result.usage_metadata:
    token_usage = {
        'input_tokens': result.usage_metadata.get('input_tokens', 0),
        'output_tokens': result.usage_metadata.get('output_tokens', 0),
        'total_tokens': result.usage_metadata.get('total_tokens', 0)
    }
```

## 🔧 迁移步骤

### 步骤1：更新依赖

```bash
# 卸载旧版本
pip uninstall langchain langchain-core langchain-community langgraph

# 安装新版本
pip install -r requirements.txt
```

### 步骤2：代码更新

1. **更新 LangGraph 导入**
   ```python
   # 删除 END 导入
   from langgraph.graph import StateGraph  # 移除 END
   ```

2. **更新图结束节点**
   ```python
   # 替换所有 END 为 "__end__"
   workflow.add_edge("node_name", "__end__")
   ```

3. **更新模型调用**
   ```python
   # 替换 agenerate 为 ainvoke
   result = await model.ainvoke(messages)
   ```

### 步骤3：测试验证

```bash
# 运行兼容性测试
python -m pytest tests/test_langchain_compatibility.py -v

# 运行完整测试套件
python -m pytest tests/ -v
```

## ⚠️ 注意事项

### 破坏性变更

1. **LangGraph END 常量删除**
   - 必须替换为 `"__end__"` 字符串
   - 影响所有使用 LangGraph 的智能体

2. **模型 API 变更**
   - `agenerate` 方法已废弃
   - 必须使用 `ainvoke` 替代

3. **响应格式变更**
   - Token 统计信息结构变更
   - 需要更新相关解析代码

### 兼容性检查

在升级后，请确保：

1. 所有智能体都能正常初始化
2. 流式输出功能正常
3. Token 统计显示正确
4. 错误处理机制有效

## 📝 更新日志

### v1.1.0 (2024-12-25)
- 升级到 LangChain 0.3
- 修复 LangGraph END 常量问题
- 更新模型调用 API
- 优化流式输出处理
- 增强错误处理和日志

## 🔗 相关资源

- [LangChain 0.3 官方迁移指南](https://python.langchain.com/docs/versions/migrating_chains/)
- [LangGraph 更新日志](https://github.com/langchain-ai/langgraph/releases)
- [项目测试文档](tests/README.md)