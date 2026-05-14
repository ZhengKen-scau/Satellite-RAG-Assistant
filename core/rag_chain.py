# Satellite RAG Assistant - RAG链构建
# 负责构建和管理检索增强生成链

import time
from typing import List, Dict, Any
from app.config import settings
from core.llm_handler import LLMHandler
from core.vector_store import VectorStoreManager
from core.prompt_manager import PromptManager

class RAGChain:
    """RAG链类"""
    
    def __init__(self):
        self.llm_handler = LLMHandler()
        self.vector_store = VectorStoreManager()
    
    def retrieve_context(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        检索相关上下文
        
        Args:
            query: 查询文本
            k: 检索文档数量
            
        Returns:
            相关上下文列表
        """
        return self.vector_store.similarity_search(query, k)
    
    def generate_answer(self, query: str, context: List[Dict[str, Any]], 
                      chat_history: List[dict] = None) -> str:
        """
        基于上下文和对话历史生成答案
        
        Args:
            query: 用户查询
            context: 检索到的上下文
            chat_history: 对话历史
            
        Returns:
            生成的答案
        """
        # 构建上下文文本和元数据摘要
        context_text = "\n\n".join([doc['content'] for doc in context])
        
        # 构建元数据摘要
        metadata_summary = ""
        if context:
            sources = []
            for doc in context:
                source = doc.get('metadata', {}).get('source', '未知来源')
                page = doc.get('metadata', {}).get('page', 'N/A')
                sources.append(f"{source} (第{page}页)")
            metadata_summary = "; ".join(sources)
        
        # 使用提示词管理器构建提示词（支持多风格自动切换和对话历史）
        prompt = PromptManager.build_rag_prompt(
            query=query,
            context=context_text,
            metadata_summary=metadata_summary,
            model_name=settings.LLM_MODEL if hasattr(settings, 'LLM_MODEL') else "qwen2.5:3b",
            chat_history=chat_history  # 传递对话历史
        )
        
        return self.llm_handler.generate_response(prompt, temperature=0.7, max_tokens=2000)
    
    def query(self, query: str, k: int = 4) -> Dict[str, Any]:
        """
        完整的RAG查询流程
        
        Args:
            query: 用户查询
            k: 检索文档数量（增加到4个以提供更多上下文）
            
        Returns:
            包含答案和源文档的响应
        """
        start_time = time.time()
        
        # 检索相关上下文
        context = self.retrieve_context(query, k)
        
        # 生成答案
        answer = self.generate_answer(query, context)
        
        processing_time = time.time() - start_time
        
        return {
            "answer": answer,
            "sources": context,
            "processing_time": processing_time
        }
    
    def query_with_documents(self, query: str, documents: List[Dict[str, Any]], 
                          chat_history: List[dict] = None, top_k: int = 4, temperature: float = 0.7) -> Dict[str, Any]:
        """
        基于临时上传文档的RAG查询流程（支持对话历史）
        
        Args:
            query: 用户查询
            documents: 临时上传并处理的文档列表
            chat_history: 对话历史，格式为 [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            top_k: 检索文档数量
            temperature: 生成温度
            
        Returns:
            包含答案和源文档的响应
        """
        start_time = time.time()
        
        # 如果有上传的文档，直接使用它们作为上下文
        if documents:
            # 限制上下文数量
            context = documents[:top_k]
            # 为临时文档添加score字段（设为1.0表示完全相关）
            for doc in context:
                if 'score' not in doc:
                    doc['score'] = 1.0
        else:
            # 如果没有上传文档，从向量存储中检索
            context = self.retrieve_context(query, top_k)
        
        # 生成答案
        answer = self.generate_answer(query, context, chat_history)
        
        processing_time = time.time() - start_time
        
        return {
            "answer": answer,
            "sources": context,
            "processing_time": processing_time
        }