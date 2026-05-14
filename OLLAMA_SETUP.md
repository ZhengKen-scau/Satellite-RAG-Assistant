# Ollama 设置指南

## 安装 Ollama

1. **下载并安装 Ollama**
   - 访问 [https://ollama.com/](https://ollama.com/)
   - 下载适用于 Windows 的安装程序
   - 按照安装向导完成安装

2. **启动 Ollama 服务**
   - 打开新的命令提示符或 PowerShell 窗口
   - 运行以下命令启动服务：
     ```bash
     ollama serve
     ```
   - 保持此窗口打开（不要关闭）

3. **下载推荐的模型**
   - 在另一个命令提示符窗口中，运行：
     ```bash
     ollama pull qwen2.5:3b
     ```
   - 或者如果您偏好其他模型：
     ```bash
     ollama pull llama3.2:3b
     ```

4. **验证安装**
   - 检查可用模型：
     ```bash
     ollama list
     ```
   - 测试模型：
     ```bash
     ollama run qwen2.5:3b
     ```

## 启动 Satellite RAG Assistant

1. **确保 Ollama 服务正在运行**（步骤2中的窗口保持打开）
2. **在项目目录中启动应用**：
   ```bash
   cd "d:\develop\project\Satellite_RAG_Assistant（卫星遥感RAG助手）"
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
3. **访问界面**：
   - 打开浏览器访问 `http://127.0.0.1:8000`
   - 如果8000端口被占用，尝试8080端口

## 常见问题解决

### 问题：连接被拒绝 (ERR_CONNECTION_REFUSED)
- **原因**：Ollama 服务未启动
- **解决**：确保执行了 `ollama serve` 并保持窗口打开

### 问题：模型未找到
- **原因**：指定的模型未下载
- **解决**：执行 `ollama pull qwen2.5:3b` 下载模型

### 问题：加载时间过长
- **原因**：首次使用模型时需要加载到内存
- **解决**：耐心等待，后续请求会更快

### 问题：嵌入模型加载失败
- **原因**：网络连接问题导致无法下载 sentence-transformers 模型
- **解决**：应用已配置为使用模拟嵌入模型，不影响基本功能

## 环境变量配置

如果需要更改默认配置，请编辑 `.env` 文件：

```env
# Ollama 配置
OLLAMA_HOST=http://localhost:11434
LLM_MODEL=qwen2.5:3b

# 其他配置保持默认即可
```

> **注意**：Ollama 默认在 `http://localhost:11434` 提供 API 服务，确保此地址可访问。