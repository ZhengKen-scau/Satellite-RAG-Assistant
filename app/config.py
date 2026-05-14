"""
Satellite RAG Assistant - 应用配置模块

该模块负责管理应用程序的所有配置参数，从环境变量加载配置，
并提供全局配置实例供其他模块使用。

Author: Satellite RAG Assistant Team
Date: 2026-05-14
"""

import os
from dotenv import load_dotenv

# 加载环境变量文件
load_dotenv()


class Settings:
    """
    应用程序配置类
    
    该类封装了所有应用程序的配置参数，包括：
    - Ollama服务配置
    - 大语言模型配置  
    - 嵌入模型配置
    - 应用服务器配置
    - 向量数据库配置
    - 文档处理配置
    - LLM生成参数配置
    - 缓存配置
    
    所有配置参数都从环境变量读取，如果未设置则使用默认值。
    """
    
    # Ollama服务配置
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    """Ollama服务的主机地址，默认为 http://localhost:11434"""
    
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen2.5:3b")
    """大语言模型名称，默认使用 qwen2.5:3b 模型"""
    
    # 无Ollama模式配置（用于简化demo）
    NO_OLLAMA_MODE: bool = os.getenv("NO_OLLAMA_MODE", "false").lower() == "true"
    """是否启用无Ollama模式，默认为 False"""
    
    # 嵌入模型配置
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    """嵌入模型名称，默认使用 sentence-transformers/all-MiniLM-L6-v2"""
    
    # 应用服务器配置
    APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")
    """应用服务器主机地址，默认为 127.0.0.1"""
    
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    """应用服务器端口，默认为 8000"""
    
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    """是否启用调试模式，默认为 False"""
    
    # 向量数据库配置
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./storage/chroma_db")
    """Chroma向量数据库存储路径，默认为 ./storage/chroma_db"""
    
    # 文档处理配置
    MAX_CHUNK_SIZE: int = int(os.getenv("MAX_CHUNK_SIZE", "1000"))
    """文档分块的最大字符数，默认为 1000"""
    
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    """文档分块的重叠字符数，默认为 200"""
    
    # LLM生成参数配置
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    """LLM生成温度参数，默认为 0.7"""
    
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2000"))
    """LLM生成的最大token数，默认为 2000"""
    
    LLM_TOP_P: float = float(os.getenv("LLM_TOP_P", "0.9"))
    """LLM生成的top-p采样参数，默认为 0.9"""
    
    # 缓存配置
    CACHE_DIR: str = os.getenv("CACHE_DIR", "./storage/cache")
    """缓存目录路径，默认为 ./storage/cache"""
    
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))
    """缓存过期时间（秒），默认为 3600 秒（1小时）"""


# 全局配置实例，供其他模块导入使用
settings = Settings()