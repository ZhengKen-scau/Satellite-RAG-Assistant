# 🛰️ Satellite RAG Assistant - 卫星遥感智能问答系统

![Satellite Intelligence Platform](https://img.shields.io/badge/Platform-Satellite%20Intelligence-blue)
![Python Version](https://img.shields.io/badge/Python-3.9%2B-green)
![FastAPI](https://img.shields.io/badge/FastAPI-Web%20Framework-orange)

**Satellite RAG Assistant** 是一个专业的卫星遥感数据智能问答平台，结合了检索增强生成（RAG）技术和大语言模型，为用户提供精准的遥感领域知识问答服务。

## 🌟 核心特性

### 📚 **智能文档问答**
- **每次提问上传文件**：支持在每次提问时上传相关文档，系统基于文档内容进行针对性回答
- **多格式支持**：PDF、TXT、DOCX、遥感影像（TIFF/HDR/BIL等）、矢量数据（SHP/GeoJSON等）
- **专业领域适配**：专为卫星遥感领域优化的提示词系统

### 🎨 **现代化用户界面**
- **直观文档气泡悬浮**：文件预览显示在输入框上方，带专业图标和悬停效果
- **响应式设计**：完美适配桌面和移动设备
- **流畅交互体验**：平滑过渡动画和即时视觉反馈

### 🧠 **高级AI能力**
- **突破上下文限制**：支持长达2000 tokens的回答生成
- **多风格提示词**：6种不同风格的提示词模板（遥感专业、学术研究、简洁明了等）
- **智能文件识别**：自动识别文件类型并显示对应图标（🛰️遥感、🗺️矢量、📊数据等）

### ⚡ **高性能架构**
- **本地大模型**：基于Ollama运行qwen2.5:3b等开源大模型
- **向量检索**：ChromaDB向量数据库实现高效语义检索
- **嵌入模型**：sentence-transformers/all-MiniLM-L6-v2提供高质量文本嵌入

## 🚀 快速开始

### 系统要求
- **操作系统**: Windows 10/11, macOS, Linux
- **Python版本**: 3.9 或更高版本
- **内存**: 建议8GB以上（大模型运行需要）
- **磁盘空间**: 至少10GB可用空间

### 安装步骤

#### 1. 克隆项目
```
git clone https://github.com/your-username/Satellite_RAG_Assistant.git
cd Satellite_RAG_Assistant
```

#### 2. 安装依赖
```
pip install -r requirements.txt
```

#### 3. 安装Ollama
- **Windows**: 下载 [Ollama Windows版](https://ollama.com/download/OllamaSetup.exe)
- **macOS**: `brew install ollama`
- **Linux**: `curl -fsSL https://ollama.com/install.sh | sh`

#### 4. 下载大模型
```
# 推荐模型（约2-3GB）
ollama pull qwen2.5:3b

# 备选模型
ollama pull llama3.2:3b
```

#### 5. 启动服务
```
# 启动Ollama服务（Windows PowerShell）
ollama serve

# 在新终端启动应用
uvicorn app.main_final:app --host 127.0.0.1 --port 8000
```

### 访问应用
打开浏览器访问: **http://127.0.0.1:8000**

## 📖 使用指南

### 基本操作
1. **纯文字提问**: 直接在输入框输入问题，点击发送按钮
2. **上传文件提问**: 
   - 点击📎附件按钮或拖拽文件到输入区域
   - 输入相关问题
   - 点击发送按钮获取基于文件内容的回答
3. **删除附件**: 悬停文件预览，点击×按钮删除

### 支持的文件格式

| 类别 | 格式 | 图标 |
|------|------|------|
| **文档格式** | PDF, TXT, DOC, DOCX, MD | 📄📝🗂️ |
| **遥感影像** | TIFF, TIF, IMG, HDR, BIL, BSQ, BIP, NC, HDF, H5 | 🛰️ |
| **矢量数据** | SHP, GeoJSON, KML, KMZ, GPX | 🗺️ |
| **图像格式** | JPG, JPEG, PNG, BMP, GIF | 🖼️ |

### 示例场景

#### 遥感数据分析
```
问题: "Landsat-8的空间分辨率是多少？"
回答: 🛰️ Landsat-8卫星的空间分辨率为15米（全色波段）和30米（多光谱波段）...
```

#### 文档问答
```
上传文件: landsat8_specs.pdf
问题: "这个文件中提到的Landsat-8空间分辨率是多少？"
回答: 🛰️ 根据你提供的文档，Landsat-8卫星的空间分辨率为15米和30米...
```

## ⚙️ 配置选项

### 环境变量配置
创建 `.env` 文件来自定义配置：

```
# Ollama配置
OLLAMA_HOST=http://localhost:11434
LLM_MODEL=qwen2.5:3b

# 应用配置
APP_HOST=127.0.0.1
APP_PORT=8000
DEBUG=false

# LLM参数
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
LLM_TOP_P=0.9

# 文档处理
MAX_CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# 缓存配置
CACHE_TTL=3600
```

### 主要配置说明
- **LLM_MAX_TOKENS**: 控制回答长度（默认2000）
- **LLM_TEMPERATURE**: 控制创造性（0.1-1.0，默认0.7）
- **MAX_CHUNK_SIZE**: 文档分块大小（影响检索精度）
- **CACHE_TTL**: 缓存过期时间（秒）

## 🏗️ 项目架构

```
Satellite_RAG_Assistant/
├── app/                    # FastAPI应用核心
│   ├── main_final.py      # 主应用入口
│   └── config.py          # 配置管理
├── core/                  # 核心功能模块
│   ├── llm_handler.py     # 大模型处理器
│   ├── rag_chain.py       # RAG链实现
│   ├── prompt_manager.py  # 提示词管理器
│   └── vector_store.py    # 向量存储管理
├── frontend/              # 前端资源
│   ├── index.html         # 主页面
│   ├── app.js            # JavaScript逻辑
│   └── style.css         # 样式表
├── scripts/               # 测试脚本
│   ├── test_prompt_manager.py
│   └── test_file_upload.py
├── storage/               # 存储目录（自动生成）
│   ├── chroma_db/        # 向量数据库
│   └── cache/            # 缓存文件
├── requirements.txt       # Python依赖
├── .env                   # 环境变量模板
└── README.md             # 项目文档
```

## 🔧 故障排除

### 常见问题

#### 1. 应用无法启动
```bash
# 检查Ollama是否运行
ollama list

# 检查端口占用
netstat -ano | findstr :8000

# 清理缓存后重试
rm -rf storage/cache/*
```

#### 2. 文件上传失败
- 确保文件大小不超过50MB
- 检查文件编码（推荐UTF-8）
- 验证文件格式是否受支持

#### 3. 回答质量不佳
- 调整 `LLM_TEMPERATURE` 参数（0.3-0.9）
- 增加 `LLM_MAX_TOKENS` 值
- 确保上传的文档内容清晰完整

### 错误代码含义
- **⚠️ Ollama服务未启动**: 需要先运行 `ollama serve`
- **⚠️ 模型未找到**: 需要先下载模型 `ollama pull <model_name>`
- **❌ 处理错误**: 检查文件格式和网络连接

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发规范
- Python代码遵循PEP 8规范
- 添加类型提示和文档字符串
- 包含单元测试
- 更新README文档

## 📜 许可证

本项目采用 [MIT License](LICENSE) 开源许可。

## 📞 联系我们

如有问题或建议，请：
- 提交 Issue
- 发送邮件至: support@satellite-rag-assistant.com
- 加入我们的 Discord 社区

---

**🚀 立即开始您的卫星遥感智能问答之旅！**

# Satellite RAG Assistant（卫星遥感RAG助手）

## 项目概述
这是一个专业的卫星遥感智能问答系统，基于RAG（Retrieval-Augmented Generation）技术构建，专门用于处理和分析卫星遥感数据、文档和技术资料。

## 功能特性

### 📄 文档格式支持
- **PDF**: 完整文本提取，保留页面结构
- **TXT/Markdown**: 多编码支持（UTF-8, GBK, GB2312）
- **DOCX/DOC**: Word文档内容提取
- **CSV**: 表格数据结构分析
- **JSON**: 结构化数据解析

### 🛰️ 遥感影像格式支持
- **GeoTIFF**: 专业的地理空间栅格格式，支持坐标系、分辨率、波段等元数据提取
- **ERDAS IMG**: ERDAS IMAGINE专业遥感格式
- **ENVI HDR/BIL/BSQ/BIP**: ENVI高光谱数据格式
- **NetCDF**: 多维科学数据格式（气象、海洋、时间序列等）
- **HDF/HDF5**: 大型科学数据集格式

### 🗺️ 矢量数据格式支持
- **Shapefile**: 标准地理空间矢量格式
- **GeoJSON**: Web标准矢量格式
- **KML/KMZ**: Google Earth格式
- **GPX**: GPS轨迹数据格式

### 🖼️ 图像格式支持
- **JPG/JPEG, PNG, BMP, GIF**: 基本图像信息提取

## 技术架构
- **前端**: HTML5 + CSS3 + JavaScript (原生)
- **后端**: FastAPI + Python
- **向量数据库**: ChromaDB
- **嵌入模型**: sentence-transformers
- **大语言模型**: Ollama (qwen2.5:3b)
- **遥感数据处理**: rasterio, geopandas, netCDF4, h5py, Pillow

## 安装依赖
```
pip install -r requirements.txt
```

## 启动应用
```
python -m uvicorn app.main:app --host 127.0.0.1 --port 8080
```

## 使用说明
1. 访问 `http://127.0.0.1:8080`
2. 上传支持的文件格式
3. 提出相关问题进行智能问答
4. 系统会自动提取文件信息并提供专业回答

## 专业特性
- **统一遥感专业风格**: 所有回答均采用卫星遥感专业术语和格式
- **多轮对话记忆**: 支持基于上下文的连续问答
- **智能文件分析**: 自动识别文件类型并提取关键信息
- **错误容错机制**: 即使文件处理失败也能提供有用信息

## 系统要求
- Python 3.8+
- Ollama 运行环境
- 推荐内存: 8GB+
- 推荐存储: 10GB+ (用于缓存和临时文件)

## 贡献指南
欢迎提交Issue和Pull Request，特别是针对新的遥感数据格式支持。
