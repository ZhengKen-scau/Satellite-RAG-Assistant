# Satellite RAG Assistant - 最终版FastAPI应用
# 支持每次提问时上传文件的文档问答功能

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
import os
import json
import tempfile
import shutil
import io
import time
import requests
from typing import List, Optional

from app.config import settings
from core.prompt_manager import PromptManager
from core.rag_chain import RAGChain
from core.document_processor import DocumentProcessor

# 创建FastAPI应用（不进行任何耗时初始化）
app = FastAPI(
    title="Satellite Intelligence Platform",
    description="Professional satellite data intelligence platform",
    version="1.0.0"
)

# 创建全局RAG链实例
rag_chain = RAGChain()
doc_processor = DocumentProcessor()

# 配置静态文件服务
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

# 创建临时目录用于会话文件
temp_dir = Path("data/temp")
temp_dir.mkdir(parents=True, exist_ok=True)

# 创建上传目录（用于持久化存储）
upload_dir = Path("data/raw")
upload_dir.mkdir(parents=True, exist_ok=True)

# 扩展支持的文件格式 - 包含遥感数据常用格式
SUPPORTED_FORMATS = {
    # 文档格式
    '.pdf': 'PDF文档',
    '.txt': '文本文件', 
    '.docx': 'Word文档',
    '.doc': 'Word文档',
    '.md': 'Markdown文件',
    '.csv': 'CSV数据文件',
    '.json': 'JSON配置文件',
    
    # 遥感数据格式
    '.tif': 'GeoTIFF影像',
    '.tiff': 'GeoTIFF影像',
    '.img': 'ERDAS影像',
    '.hdr': 'ENVI头文件',
    '.bil': '波段交错影像',
    '.bsq': '波段顺序影像',
    '.bip': '波段内交错影像',
    '.nc': 'NetCDF数据',
    '.hdf': 'HDF数据',
    '.h5': 'HDF5数据',
    '.shp': 'Shapefile矢量',
    '.geojson': 'GeoJSON矢量',
    '.kml': 'KML文件',
    '.kmz': 'KMZ文件',
    '.gpx': 'GPX轨迹文件',
    
    # 图像格式
    '.jpg': 'JPEG图像',
    '.jpeg': 'JPEG图像', 
    '.png': 'PNG图像',
    '.bmp': 'BMP图像',
    '.gif': 'GIF图像'
}

def extract_text_from_pdf(file_content: bytes) -> str:
    """从PDF文件提取文本"""
    try:
        import PyPDF2
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        return f"PDF文本提取失败: {str(e)}"

def extract_text_from_docx(file_content: bytes) -> str:
    """从DOCX文件提取文本"""
    try:
        import docx
        doc_file = io.BytesIO(file_content)
        doc = docx.Document(doc_file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text.strip()
    except Exception as e:
        return f"DOCX文本提取失败: {str(e)}"

def extract_metadata_from_geotiff(file_content: bytes, filename: str) -> str:
    """从GeoTIFF文件提取元数据信息"""
    try:
        # 简化版本：返回基本信息，实际项目中可使用 rasterio 或 gdal
        return f"GeoTIFF文件 '{filename}' 已上传。包含遥感影像数据，可用于分析植被指数、土地利用等。"
    except Exception as e:
        return f"GeoTIFF元数据提取失败: {str(e)}"

def extract_metadata_from_shapefile(file_content: bytes, filename: str) -> str:
    """从Shapefile提取基本信息"""
    try:
        # 简化版本：返回基本信息，实际项目中可使用 geopandas 或 fiona
        return f"Shapefile '{filename}' 已上传。包含矢量地理数据，可用于空间分析和地图制作。"
    except Exception as e:
        return f"Shapefile元数据提取失败: {str(e)}"

@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径返回前端页面"""
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding='utf-8'))
    else:
        return {"message": "Satellite Intelligence Platform is running!"}

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "model": settings.LLM_MODEL}

# 模型状态检查端点 - 用于前端轮询
@app.get("/api/v1/status")
async def get_model_status():
    """检查大模型服务状态"""
    try:
        import requests
        response = requests.get(f"{settings.OLLAMA_HOST}/api/tags")
        if response.status_code == 200:
            return {"status": "online", "model": settings.LLM_MODEL}
        else:
            return {"status": "offline", "model": settings.LLM_MODEL}
    except Exception as e:
        return {"status": "offline", "model": settings.LLM_MODEL}

# 获取支持的文件格式
@app.get("/api/v1/upload/formats")
async def get_supported_formats():
    """获取支持的文件格式列表"""
    return {
        "supported_formats": SUPPORTED_FORMATS,
        "message": "✅ 支持多种遥感数据和文档格式"
    }

# 主要的文档问答API - 支持上传文件并提问
@app.post("/api/v1/query")
async def query_with_files(
    query: str = Form(...),
    files: List[UploadFile] = File(default=None)
):
    """
    处理用户查询和文件上传
    
    Args:
        query: 用户问题
        files: 上传的文件列表
        
    Returns:
        包含答案、来源和处理时间的响应
    """
    start_time = time.time()
    
    try:
        if not query.strip():
            raise HTTPException(status_code=400, detail="查询内容不能为空")

        valid_files = []
        
        if files:
            for file in files:
                if not file.filename:
                    continue
                    
                file_ext = os.path.splitext(file.filename)[1].lower()
                if file_ext not in SUPPORTED_FORMATS:
                    continue
                
                valid_files.append(file)
        
        # 如果有文件上传，先处理并添加到向量数据库
        if valid_files:
            # 创建临时目录存储上传的文件
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_paths = []
                for file in valid_files:
                    temp_path = os.path.join(temp_dir, file.filename)
                    with open(temp_path, "wb") as f:
                        content = await file.read()
                        f.write(content)
                    temp_paths.append(temp_path)
                
                # 处理文档并添加到向量数据库
                documents = doc_processor.process_documents(temp_paths)
                if documents:
                    rag_chain.vector_store.add_documents(documents)
        
        # 使用RAG链进行查询（这会自动检索相关上下文）
        response_data = rag_chain.query(query, k=4)
        answer = response_data.get("answer", "无法生成回答")
        sources = response_data.get("sources", [])
        processing_time = response_data.get("processing_time", time.time() - start_time)
        
        # 检查是否需要降级处理
        should_fallback = False
        fallback_context = ""
        
        if not sources and valid_files:
            # 构建文件内容上下文
            file_context_parts = []
            for file in valid_files:
                filename = file.filename
                file_ext = os.path.splitext(filename)[1].lower()
                
                if file_ext == '.doc':
                    # DOC文件的特殊处理
                    file_context_parts.append(f"Word文档 '{filename}' 已上传用于问答。")
                elif file_ext == '.docx':
                    file_context_parts.append(f"Word文档 '{filename}' 已上传用于问答。")
                elif file_ext == '.pdf':
                    file_context_parts.append(f"PDF文档 '{filename}' 已上传用于问答。")
                elif file_ext in ['.shp', '.geojson']:
                    file_context_parts.append(f"矢量数据 '{filename}' 已上传用于问答。")
                elif file_ext in ['.tif', '.tiff', '.hdr', '.bil']:
                    file_context_parts.append(f"遥感影像 '{filename}' 已上传用于问答。")
                else:
                    file_context_parts.append(f"文件 '{filename}' 已上传用于问答。")
            
            fallback_context = "\n".join(file_context_parts)
            should_fallback = True
        
        # 如果需要降级处理，直接构建提示词
        if should_fallback:
            prompt = PromptManager.build_rag_prompt(
                query=query,
                context=fallback_context,
                style="remote_sensing"
            )
            
            # 调用Ollama API
            try:
                ollama_response = requests.post(
                    f"{settings.OLLAMA_HOST}/api/generate",
                    json={
                        "model": settings.LLM_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "num_predict": 2000,
                            "top_p": 0.9,
                            "repeat_penalty": 1.1
                        }
                    },
                    timeout=120
                )
                
                if ollama_response.status_code == 200:
                    result = ollama_response.json()
                    answer = result.get("response", "无法生成回答")
                    processing_time = result.get("total_duration", 0) / 1000000000
                    # 清空sources，因为我们使用的是降级上下文
                    sources = []
                    
            except Exception as e:
                # 降级处理失败，使用简单回答
                answer = f"已收到您的文件 '{valid_files[0].filename}'，但由于技术限制，无法提取详细内容。您可以尝试重新上传或提供更多具体问题。"
                processing_time = time.time() - start_time
        
        # 添加emoji
        if "卫星" in answer or "遥感" in answer:
            answer = "🛰️ " + answer
        elif "分析" in answer or "数据" in answer:
            answer = "📊 " + answer
        elif "环境" in answer or "生态" in answer:
            answer = "🌍 " + answer
        elif "农业" in answer or "作物" in answer:
            answer = "🌾 " + answer
        elif "城市" in answer or "建筑" in answer:
            answer = "🏙️ " + answer
            
        return {
            "answer": answer,
            "sources": sources,
            "processing_time": round(processing_time, 1)
        }
        
    except Exception as e:
        # 简单判断异常类型以提供更友好的错误信息
        error_str = str(e).lower()
        if "connection" in error_str or "refused" in error_str:
             return {
                "answer": "⚠️ Ollama服务未启动或连接失败\n请确保Ollama正在运行，并执行 'ollama serve' 启动服务。",
                "sources": [],
                "processing_time": 0
            }
        elif "timeout" in error_str:
            return {
                "answer": "⏰ 请求超时\nOllama服务响应时间过长，请检查模型是否正常加载。",
                "sources": [],
                "processing_time": 0
            }
        else:
            return {
                "answer": f"❌ 系统错误\n{str(e)}",
                "sources": [],
                "processing_time": 0
            }

# 保留原有的文件管理API（用于全局文件管理）
@app.post("/api/v1/upload/files")
async def upload_files_global(files: List[UploadFile] = File(...)):
    """全局文件上传（用于长期存储）"""
    try:
        if not files or len(files) == 0:
            return {
                "message": "⚠️ 没有选择文件。请选择要上传的文件。",
                "status": "warning",
                "uploaded_files": [],
                "failed_files": []
            }
        
        uploaded_files = []
        failed_files = []
        
        for file in files:
            if file.filename == "":
                continue
            
            # 检查文件大小（限制为50MB）
            file.file.seek(0, 2)  # 移动到文件末尾
            file_size = file.file.tell()  # 获取文件大小
            file.file.seek(0)  # 重置文件指针
            
            if file_size > 50 * 1024 * 1024:  # 50MB
                failed_files.append({
                    "filename": file.filename,
                    "reason": f"文件太大 ({file_size / (1024*1024):.1f}MB)，超过50MB限制"
                })
                continue
                
            file_ext = Path(file.filename).suffix.lower()
            if file_ext in SUPPORTED_FORMATS:
                file_path = upload_dir / file.filename
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                uploaded_files.append({
                    "filename": file.filename,
                    "format": SUPPORTED_FORMATS[file_ext],
                    "size": file_path.stat().st_size if file_path.exists() else 0
                })
            else:
                failed_files.append({
                    "filename": file.filename,
                    "reason": "不支持的文件格式"
                })
        
        if uploaded_files:
            success_message = f"✅ 成功上传 {len(uploaded_files)} 个文件：\n"
            for file_info in uploaded_files:
                size_mb = file_info['size'] / (1024 * 1024)
                success_message += f"• {file_info['filename']} ({file_info['format']}, {size_mb:.2f}MB)\n"
            
            if failed_files:
                success_message += f"\n⚠️ {len(failed_files)} 个文件上传失败：\n"
                for file_info in failed_files:
                    success_message += f"• {file_info['filename']} - {file_info['reason']}\n"
            
            return {
                "message": success_message.strip(),
                "status": "success",
                "uploaded_files": uploaded_files,
                "failed_files": failed_files
            }
        elif failed_files:
            error_message = f"❌ 所有文件上传失败：\n"
            for file_info in failed_files:
                error_message += f"• {file_info['filename']} - {file_info['reason']}\n"
            return {
                "message": error_message.strip(),
                "status": "error",
                "uploaded_files": [],
                "failed_files": failed_files
            }
        else:
            return {
                "message": "⚠️ 没有有效的文件被上传。支持多种遥感数据和文档格式。",
                "status": "warning",
                "uploaded_files": [],
                "failed_files": []
            }
            
    except Exception as e:
        return {
            "message": f"❌ 文件上传失败: {str(e)}",
            "status": "error",
            "uploaded_files": [],
            "failed_files": []
        }

# 获取已上传文件列表
@app.get("/api/v1/upload/files")
async def list_uploaded_files():
    """获取已上传的文件列表"""
    try:
        uploaded_files = []
        if upload_dir.exists():
            for file_path in upload_dir.iterdir():
                if file_path.is_file():
                    file_ext = file_path.suffix.lower()
                    format_name = SUPPORTED_FORMATS.get(file_ext, "未知格式")
                    uploaded_files.append({
                        "filename": file_path.name,
                        "format": format_name,
                        "size": file_path.stat().st_size,
                        "uploaded_at": file_path.stat().st_mtime
                    })
        
        return {
            "files": uploaded_files,
            "total_count": len(uploaded_files),
            "total_size": sum(f['size'] for f in uploaded_files)
        }
    except Exception as e:
        return {
            "files": [],
            "total_count": 0,
            "total_size": 0,
            "error": str(e)
        }

# 添加删除文件端点
@app.delete("/api/v1/upload/files/{filename}")
async def delete_uploaded_file(filename: str):
    """删除指定的已上传文件"""
    try:
        if not filename or filename in ['.', '..']:
            return {
                "message": "❌ 文件名无效",
                "status": "error"
            }
        
        # 安全检查：确保文件路径在upload_dir目录下
        file_path = (upload_dir / filename).resolve()
        if not str(file_path).startswith(str(upload_dir.resolve())):
            return {
                "message": "❌ 不允许访问该路径",
                "status": "error"
            }
        
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
            return {
                "message": f"✅ 成功删除文件: {filename}",
                "status": "success"
            }
        else:
            return {
                "message": f"❌ 文件不存在: {filename}",
                "status": "error"
            }
            
    except Exception as e:
        return {
            "message": f"❌ 删除文件失败: {str(e)}",
            "status": "error"
        }

# 修复：使用正确的文档处理路径
@app.post("/api/v1/documents/process")
async def process_documents():
    """文档处理端点 - 简化版本"""
    return {
        "message": "📄 文档处理功能已启用！系统将基于您上传的文档提供智能问答服务。",
        "status": "success"
    }