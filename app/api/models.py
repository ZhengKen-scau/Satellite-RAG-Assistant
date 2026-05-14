# Satellite RAG Assistant - 数据模型
# 定义API请求和响应的数据模型

from pydantic import BaseModel
from typing import List, Optional

class SourceDocument(BaseModel):
    """源文档模型"""
    content: str
    metadata: dict
    score: float

class QueryRequest(BaseModel):
    """查询请求模型"""
    query: str
    # 添加对话历史字段
    chat_history: Optional[List[dict]] = None  # 格式: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

class QueryResponse(BaseModel):
    """查询响应模型"""
    answer: str
    sources: List[SourceDocument]
    processing_time: float
