# Satellite RAG Assistant - 向量数据库管理
# 负责向量存储的创建、管理和检索操作

import os
import uuid
import chromadb
from typing import List, Dict, Any
from app.config import settings
from core.llm_handler import LLMHandler

class VectorStoreManager:
    """向量存储管理器"""
    
    def __init__(self):
        self.llm_handler = LLMHandler()
        # 使用唯一标识符确保每次会话使用新的集合
        session_id = str(uuid.uuid4())[:8]
        collection_name = f"satellite_rag_{session_id}"
        
        # 创建Chroma客户端
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_PATH
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        向向量数据库添加文档
        
        Args:
            documents: 要添加的文档列表，每个文档应包含'content'和'metadata'字段
        """
        if not documents:
            return
        
        ids = [f"doc_{i}" for i in range(len(documents))]
        contents = [doc['content'] for doc in documents]
        metadatas = [doc.get('metadata', {}) for doc in documents]
        
        # 生成嵌入向量
        embeddings = []
        for content in contents:
            embedding = self.llm_handler.embed_text(content)
            embeddings.append(embedding)
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas
        )
    
    def similarity_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        执行相似性搜索
        
        Args:
            query: 查询文本
            k: 返回结果数量
            
        Returns:
            相似文档列表
        """
        query_embedding = self.llm_handler.embed_text(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        documents = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'score': results['distances'][0][i] if results['distances'] else 0.0
                })
        
        return documents
    
    def delete_collection(self):
        """删除整个集合"""
        try:
            self.client.delete_collection("satellite_documents")
            self.collection = self.client.get_or_create_collection(
                name="satellite_documents",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"删除集合时出错: {e}")