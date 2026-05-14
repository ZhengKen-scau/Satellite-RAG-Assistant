# Satellite RAG Assistant - API路由定义
# 定义所有API端点和请求处理逻辑

import os
import tempfile
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from typing import List, Optional
from app.api.models import QueryRequest, QueryResponse
from core.rag_chain import RAGChain
from core.document_processor import DocumentProcessor
from app.config import settings
import logging
import json
import requests

# 添加logger
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/status")
async def get_model_status():
    """获取模型状态"""
    try:
        # 检查Ollama服务是否在线
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            return {"status": "online", "model": settings.LLM_MODEL}
        else:
            return {"status": "offline", "model": settings.LLM_MODEL}
    except Exception as e:
        logger.error(f"检查模型状态失败: {e}")
        return {"status": "offline", "model": settings.LLM_MODEL}

# 延迟初始化RAG链 - 避免模块导入时的耗时操作
_rag_chain = None

def get_rag_chain():
    """获取RAG链实例（延迟初始化）"""
    global _rag_chain
    if _rag_chain is None:
        _rag_chain = RAGChain()
    return _rag_chain

@router.post("/query", response_model=QueryResponse)
async def query_rag(
    query: str = Form(...),
    files: List[UploadFile] = File(default=[]),
    chat_history: str = Form(default="[]"),  # JSON字符串格式的对话历史
    top_k: int = Form(3),
    temperature: float = Form(0.7)
):
    """
    RAG查询端点（支持文件上传和对话历史）
    接收用户查询、可选的文件和对话历史，并返回基于卫星遥感文档的智能回答
    """
    try:
        # 解析对话历史
        try:
            chat_history_list = json.loads(chat_history)
            if not isinstance(chat_history_list, list):
                chat_history_list = []
        except (json.JSONDecodeError, TypeError):
            chat_history_list = []
        
        # 处理上传的文件（如果有）
        temp_files = []
        documents = []
        
        if files:
            # 创建临时目录保存上传的文件
            with tempfile.TemporaryDirectory() as temp_dir:
                # 保存上传的文件到临时目录
                for file in files:
                    if file.filename:
                        temp_file_path = os.path.join(temp_dir, file.filename)
                        with open(temp_file_path, "wb") as buffer:
                            content = await file.read()
                            buffer.write(content)
                        temp_files.append(temp_file_path)
                
                # 如果有临时文件，处理它们
                if temp_files:
                    processor = DocumentProcessor()
                    documents = processor.process_documents(temp_files)
                    logger.info(f"Processed documents: {documents}")
        
        # 执行查询
        rag_chain = get_rag_chain()
        logger.info(f"Documents before query: {documents}")
        result = rag_chain.query_with_documents(
            query=query,
            documents=documents,
            chat_history=chat_history_list,  # 传递对话历史
            top_k=top_k,
            temperature=temperature
        )
        logger.info(f"Query result: {result}")
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            processing_time=result["processing_time"]
        )
        
    except Exception as e:
        # 记录详细错误信息
        logger.error(f"查询处理失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询处理失败: {str(e)}")

@router.post("/documents/process")
async def process_documents(background_tasks: BackgroundTasks):
    """
    文档处理端点
    触发文档处理流程，将原始文档转换为向量存储
    """
    try:
        async def process_task():
            processor = DocumentProcessor()
            rag_chain = get_rag_chain()
            vector_store = rag_chain.vector_store
            
            # 处理原始文档目录
            raw_dir = "data/raw"
            if os.path.exists(raw_dir):
                documents = processor.process_directory(raw_dir)
                if documents:
                    vector_store.add_documents(documents)
        
        background_tasks.add_task(process_task)
        return {"message": "文档处理任务已启动"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档处理启动失败: {str(e)}")