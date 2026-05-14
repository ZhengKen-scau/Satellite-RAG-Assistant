# Satellite RAG Assistant - 卫星遥感智能问答系统

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Web_Framework-orange)](https://fastapi.tiangolo.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-green)](https://ollama.com/)
[![MIT License](https://img.shields.io/badge/License-MIT-red)](LICENSE)

**Satellite RAG Assistant** 是一个专业的卫星遥感数据智能问答平台，结合检索增强生成（RAG）技术和大语言模型，为用户提供精准的遥感领域知识问答服务。

**联系邮箱**: 3377374180@qq.com

---

## 技术路线与架构设计

### 整体技术架构

本项目采用典型的RAG（Retrieval-Augmented Generation）架构，将传统的信息检索技术与现代大语言模型相结合。系统架构分为四个核心层次：

1. **数据输入层**: 支持多格式文件上传和文本输入
2. **文档处理层**: 文件解析、文本提取、向量化处理
3. **检索增强层**: 向量数据库存储、语义相似度检索
4. **生成输出层**: 大语言模型推理、专业回答生成

```
用户输入 → 文档处理器 → 向量数据库 → 语义检索 → 提示词构建 → LLM生成 → 专业回答
```

### 核心技术栈

| 组件 | 技术选型 | 版本 |
|------|----------|------|
| Web框架 | FastAPI | 0.104.0+ |
| 前端技术 | HTML5/CSS3/JavaScript | 原生 |
| 向量数据库 | ChromaDB | 0.4.22+ |
| 嵌入模型 | sentence-transformers/all-MiniLM-L6-v2 | - |
| 大语言模型 | Ollama + qwen2.5:3b | - |
| 遥感数据处理 | rasterio, geopandas, netCDF4, h5py | - |
| 文档处理 | PyPDF2, python-docx, pandas | - |

---

## 技术选型理由

### 为什么选择RAG架构？

**问题背景**: 传统大语言模型存在知识截止、幻觉问题和领域专业性不足等限制。在卫星遥感这一高度专业化的领域，通用模型难以提供准确、可靠的技术解答。

**解决方案**: RAG架构通过以下优势解决上述问题：
- **知识实时性**: 通过上传最新技术文档，确保回答基于最新资料
- **减少幻觉**: 强制模型基于检索到的真实上下文生成回答
- **领域专业化**: 结合遥感专业术语和知识体系，提升回答准确性
- **数据隐私**: 本地部署方案，敏感遥感数据无需上传云端

### 为什么选择FastAPI？

- **高性能**: 基于Starlette和Pydantic，性能接近Node.js和Go
- **类型安全**: 内置Pydantic验证，减少运行时错误
- **自动生成文档**: 自动生成交互式API文档，便于调试和维护
- **异步支持**: 原生支持async/await，适合I/O密集型任务
- **轻量级**: 无复杂依赖，部署简单

### 为什么选择Ollama + qwen2.5:3b？

**Ollama优势**:
- **本地部署**: 模型完全运行在本地，保障数据安全
- **简化管理**: 统一的模型管理和API接口
- **资源优化**: 自动GPU加速，内存占用相对较低
- **开源免费**: 无商业授权费用

**qwen2.5:3b优势**:
- **中文优化**: 通义千问系列专为中文场景优化
- **遥感适配**: 在技术文档理解方面表现优秀
- **参数规模**: 3B参数在性能和资源消耗间取得平衡
- **开源许可**: 允许商业使用和修改

### 为什么选择ChromaDB？

- **Python原生**: 与Python生态无缝集成
- **本地存储**: 支持持久化本地向量存储
- **简单易用**: API简洁，学习成本低
- **社区活跃**: 持续更新和bug修复
- **性能良好**: 对中小规模数据集性能优异

### 为什么选择sentence-transformers？

- **离线可用**: 无需网络连接，完全本地运行
- **高质量嵌入**: 在中文文本嵌入任务中表现优秀
- **预训练模型**: 提供多种预训练模型选择
- **轻量高效**: 模型体积小，推理速度快

---

## 技术实现过程

### 1. 系统初始化阶段

**配置管理**: 
- 采用环境变量驱动的配置模式，通过`.env`文件管理所有参数
- 实现`Settings`类统一管理配置，避免硬编码
- 支持动态配置更新，无需重启服务

**依赖抑制**:
- 设置`TRANSFORMERS_NO_ADVISORY_WARNINGS=true`抑制警告
- 设置`TOKENIZERS_PARALLELISM=false`避免并行警告
- 延迟初始化嵌入模型，减少启动时间

### 2. 文档处理流程

**多格式支持实现**:
```python
# 文档处理器根据文件扩展名调用不同解析器
if file_ext == '.pdf':
    text = extract_text_from_pdf(file_content)
elif file_ext in ['.shp', '.geojson']:
    metadata = extract_metadata_from_shapefile(file_content, filename)
elif file_ext in ['.tif', '.tiff']:
    metadata = extract_metadata_from_geotiff(file_content, filename)
```

**文本分块策略**:
- 采用固定大小分块（默认1000字符）配合重叠（默认200字符）
- 平衡检索精度和上下文完整性
- 支持配置调整以适应不同文档类型

### 3. RAG核心实现

**检索流程**:
1. 用户查询通过嵌入模型转换为向量
2. 在ChromaDB中检索最相似的k个文档片段
3. 将检索结果按相关性排序并组合

**提示词构建**:
- 采用专业遥感领域模板
- 强制中文输出，禁止英文回答
- 包含上下文引用和专业术语规范

**生成控制**:
- 温度参数：0.7（平衡创造性和准确性）
- 最大token数：2000（支持长篇专业回答）
- Top-p采样：0.9（保证多样性）

### 4. 前后端交互设计

**API设计**:
- POST `/api/v1/query`: 主要问答接口，支持文件上传
- GET `/health`: 健康检查接口
- GET `/api/v1/status`: 模型状态检查
- GET `/api/v1/upload/formats`: 支持格式列表

**前端实现**:
- 原生JavaScript实现，无构建步骤
- 支持拖拽上传和文件预览
- 实时显示上传进度和处理状态
- 响应式设计，适配移动设备

### 5. 错误处理与降级机制

**异常处理层级**:
- 文件解析异常：返回格式不支持提示
- 模型连接异常：提示Ollama服务状态
- 网络超时异常：提供重试建议
- 内存不足异常：建议降低参数配置

**降级策略**:
- 当无相关上下文时，返回"根据提供的资料，我无法找到相关答案"
- 当文件处理失败时，仍尝试基于文件名提供基本信息
- 支持无Ollama模式，提供模拟响应用于演示

---

## 核心特性

### 智能文档问答系统

- **动态文件上传**: 每次提问可上传不同文件，实现针对性问答
- **全格式支持**: 
  - **文档格式**: PDF、TXT、DOCX、DOC、Markdown、CSV、JSON
  - **遥感影像**: GeoTIFF、ERDAS IMG、ENVI HDR/BIL、NetCDF、HDF/HDF5
  - **矢量数据**: Shapefile、GeoJSON、KML/KMZ、GPX
  - **图像格式**: JPG、PNG、BMP、GIF
- **专业领域适配**: 专为卫星遥感领域优化的回答风格

### 企业级架构设计

- **配置驱动**: 所有参数通过.env文件管理，无硬编码
- **错误容错**: 完善的异常处理和用户友好提示
- **性能优化**: 缓存机制、延迟加载、资源释放
- **安全考虑**: 本地部署保障数据隐私
- **可扩展性**: 模块化设计，便于功能扩展

---

## 快速开始

### 系统要求
- **操作系统**: Windows 10/11, macOS, Linux
- **Python版本**: 3.9 或更高版本
- **内存**: 建议8GB以上（大模型运行需要）
- **磁盘空间**: 至少10GB可用空间

### 一键部署
```bash
# 1. 克隆项目
git clone https://github.com/your-username/Satellite_RAG_Assistant.git
cd Satellite_RAG_Assistant

# 2. 安装依赖
pip install -r requirements.txt

# 3. 安装Ollama (Windows示例)
# 下载: https://ollama.com/download/OllamaSetup.exe

# 4. 下载推荐模型 (~2GB)
ollama pull qwen2.5:3b

# 5. 启动应用 (自动处理端口冲突)
python run_simple.py
```

### 访问应用
打开浏览器访问: **http://127.0.0.1:8000**

---

## 项目价值定位

### 简历项目优势
- **技术栈前沿**: 集成RAG、大语言模型、向量数据库等热门AI技术
- **领域专业性**: 聚焦卫星遥感这一高价值垂直领域，展现专业深度
- **完整产品思维**: 包含前端界面、后端API、数据处理全流程
- **可演示性强**: 本地部署即可运行，面试时可现场展示
- **代码质量高**: 规范化注释、类型提示、错误处理，体现工程素养

### 研究基础价值
- **模块化架构**: 核心组件解耦，便于替换和扩展
- **多格式支持**: 完整的遥感数据处理框架，可扩展新格式
- **提示词工程**: 专业的遥感领域提示词模板，可研究优化
- **性能可调**: 丰富的配置参数，适合性能调优研究
- **开源友好**: MIT许可证，可自由修改和商业化使用

---

## 自定义与扩展

### 修改默认模型
```bash
# .env 文件
LLM_MODEL=llama3.2:3b
```

### 调整回答长度
```bash
# .env 文件
LLM_MAX_TOKENS=3000  # 默认2000
```

### 添加新文件格式
1. 在 `core/document_processor.py` 中添加解析逻辑
2. 在 `frontend/app.js` 中添加文件图标
3. 更新 `README.md` 中的支持格式列表

### 扩展提示词风格
修改 `core/prompt_manager.py` 中的模板，支持更多专业场景。

---

## 许可证

本项目采用 [MIT License](LICENSE) 开源许可，允许商业使用、修改、分发和私有使用。

---

## 联系方式

**项目维护**: 3377374180@qq.com  
**Issues**: 提交bug报告和功能请求  
**Pull Requests**: 欢迎贡献代码

---

**立即开始您的卫星遥感智能问答之旅！**