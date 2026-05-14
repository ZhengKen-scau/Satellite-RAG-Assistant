"""
Satellite RAG Assistant - 大语言模型处理器模块

该模块负责与大语言模型（LLM）的交互和管理，包括：
- Ollama服务连接管理
- 嵌入模型加载和管理
- 文本嵌入生成
- LLM对话生成
- 无Ollama模式的降级处理

Author: Satellite RAG Assistant Team
Date: 2025-05-13
"""

from typing import List, Dict, Any
import ollama
import requests
import time
from app.config import settings


class LLMHandler:
    """
    大语言模型处理器类
    
    该类封装了与大语言模型交互的所有功能，支持Ollama本地模型和无Ollama模式。
    主要功能包括：
    - 模型连接状态检查
    - 文本嵌入向量生成
    - 对话消息生成
    - 错误处理和降级机制
    
    Attributes:
        model_name (str): 使用的大语言模型名称
        embedding_model_name (str): 使用的嵌入模型名称
        ollama_host (str): Ollama服务地址
        no_ollama_mode (bool): 是否启用无Ollama模式
        _embedding_model: 延迟初始化的嵌入模型实例
    """
    
    def __init__(self):
        """
        初始化LLM处理器
        
        从配置中加载模型参数，设置环境变量以抑制不必要的日志输出，
        并初始化Ollama客户端连接（如果在非无Ollama模式下）。
        """
        self.model_name = settings.LLM_MODEL
        self.embedding_model_name = settings.EMBEDDING_MODEL
        self.ollama_host = settings.OLLAMA_HOST
        self.no_ollama_mode = settings.NO_OLLAMA_MODE
        
        # 抑制transformers库的进度条和警告输出
        import os
        os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = 'true'
        os.environ['TOKENIZERS_PARALLELISM'] = 'false'
        
        # 延迟初始化嵌入模型，在第一次使用时加载
        self._embedding_model = None
        
        # 配置Ollama客户端（仅在非无Ollama模式下）
        if not self.no_ollama_mode:
            ollama.base_url = self.ollama_host
    
    def check_ollama_connection(self, timeout: int = 2) -> bool:
        """
        检查Ollama服务连接状态
        
        Args:
            timeout (int): 连接超时时间（秒），默认为2秒
            
        Returns:
            bool: 如果连接成功返回True，否则返回False。在无Ollama模式下始终返回False。
        """
        if self.no_ollama_mode:
            return False
            
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=timeout)
            return response.status_code == 200
        except Exception:
            return False
    
    def check_model_available(self, timeout: int = 2) -> bool:
        """
        检查指定模型是否在Ollama中可用
        
        Args:
            timeout (int): 请求超时时间（秒），默认为2秒
            
        Returns:
            bool: 如果模型可用返回True，否则返回False
        """
        if self.no_ollama_mode:
            return False
            
        try:
            if not self.check_ollama_connection(timeout):
                return False
            
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=timeout)
            if response.status_code == 200:
                models = response.json().get('models', [])
                for model in models:
                    if model.get('name') == self.model_name:
                        return True
            return False
        except Exception:
            return False
    
    @property
    def embedding_model(self):
        """
        获取嵌入模型实例（延迟初始化）
        
        尝试加载配置的嵌入模型。如果离线加载失败，则尝试在线加载。
        如果都失败，则返回一个模拟的嵌入模型实例以避免程序崩溃。
        
        Returns:
            SentenceTransformer | MockEmbeddingModel: 嵌入模型实例
        """
        if self._embedding_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                # 尝试离线加载（如果模型已缓存），并抑制进度条
                self._embedding_model = SentenceTransformer(
                    self.embedding_model_name, 
                    local_files_only=True,
                    show_progress_bar=False
                )
            except Exception:
                try:
                    # 尝试在线加载，同样抑制进度条
                    from sentence_transformers import SentenceTransformer
                    self._embedding_model = SentenceTransformer(
                        self.embedding_model_name,
                        show_progress_bar=False
                    )
                except Exception:
                    # 创建一个简单的模拟嵌入模型，避免启动时的网络请求
                    self._embedding_model = MockEmbeddingModel()
        return self._embedding_model
    
    def generate_response(self, prompt: str, temperature: float = None, max_tokens: int = None) -> str:
        """
        基于提示词生成单轮文本响应
        
        Args:
            prompt (str): 用户输入的提示词
            temperature (float, optional): 温度参数，控制随机性。默认为配置值。
            max_tokens (int, optional): 最大生成token数。默认为配置值。
            
        Returns:
            str: 生成的文本响应。如果出错或服务不可用，返回错误提示信息。
        """
        # 使用配置文件中的默认值
        if temperature is None:
            temperature = settings.LLM_TEMPERATURE
        if max_tokens is None:
            max_tokens = settings.LLM_MAX_TOKENS
        
        # 如果启用无Ollama模式，返回模拟响应
        if self.no_ollama_mode:
            return self._generate_mock_response(prompt)
        
        # 检查Ollama连接（快速超时）
        if not self.check_ollama_connection(timeout=1):
            return "⚠️ Ollama服务未启动\n请确保Ollama正在运行，并执行 'ollama serve' 启动服务。"
        
        # 检查模型是否可用
        if not self.check_model_available(timeout=1):
            return f"⚠️ 模型 '{self.model_name}' 未找到\n请执行 'ollama pull {self.model_name}' 下载模型。"
        
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    'temperature': temperature,
                    'num_predict': max_tokens,
                    'top_p': settings.LLM_TOP_P,
                    'repeat_penalty': 1.1  # 轻微重复惩罚避免冗余
                }
            )
            raw_response = response['response']
            # 后处理：替换通用AI身份回答
            processed_response = self._post_process_response(raw_response)
            return processed_response
        except Exception as e:
            error_msg = str(e).lower()
            if "not found" in error_msg:
                return f"⚠️ 模型 '{self.model_name}' 未找到\n请执行 'ollama pull {self.model_name}' 下载模型。"
            elif "connection" in error_msg or "refused" in error_msg or "timeout" in error_msg:
                return "⚠️ 无法连接到Ollama服务\n请确保Ollama正在运行。"
            else:
                return f"⚠️ 生成文本时出错\n{str(e)}"
    
    def _post_process_response(self, response: str) -> str:
        """
        后处理模型响应，替换不符合卫星遥感助手身份的内容
        
        Args:
            response (str): 模型原始生成的响应文本
            
        Returns:
            str: 处理后的响应文本
        """
        # 检测并替换通用AI身份介绍
        identity_patterns = [
            "我是Qwen",
            "我是一个由阿里云开发的AI助手",
            "我是通义千问",
            "我是阿里云开发的",
            "Qwen，一个由阿里云开发的AI助手",
            "我是Qwen，一个阿里云开发的AI助手"
        ]
        
        for pattern in identity_patterns:
            if pattern in response:
                return "我是卫星遥感智能助手，专门为您提供卫星遥感数据分析和地理信息服务。"
        
        # 如果回答包含"Qwen"或"阿里云"且与身份相关，也进行替换
        if any(keyword in response.lower() for keyword in ["qwen", "阿里云", "通义千问"]) and ("我是" in response or "你是" in response):
            return "我是卫星遥感智能助手，专门为您提供卫星遥感数据分析和地理信息服务。"
            
        return response
    
    def _generate_mock_response(self, prompt: str) -> str:
        """
        生成模拟响应用于Demo展示或无Ollama模式
        
        Args:
            prompt (str): 用户输入的提示词
            
        Returns:
            str: 模拟的响应文本
        """
        # 根据提示词生成简单的模拟响应
        if "卫星" in prompt or "遥感" in prompt or "satellite" in prompt.lower():
            return "这是一个卫星遥感数据智能分析系统的演示回复。系统能够处理卫星影像数据，提供地理信息分析和环境监测功能。在实际应用中，这里会显示由大语言模型生成的专业分析结果。"
        elif "rag" in prompt.lower() or "检索" in prompt:
            return "RAG（检索增强生成）系统已成功处理您的查询。系统从文档库中检索相关信息，并结合大语言模型生成准确的回答。这是一个简化的演示版本。"
        elif "你好" in prompt or "hello" in prompt.lower():
            return "您好！欢迎使用卫星遥感智能助手演示系统。这是一个用于简历展示的简化版本，展示了RAG系统的基本架构和功能。"
        else:
            return "感谢您的查询！这是卫星遥感RAG助手的演示回复。系统集成了文档检索、向量数据库和智能问答功能，专为地理空间数据分析设计。"

    def embed_text(self, text: str) -> List[float]:
        """
        生成单段文本的嵌入向量
        
        Args:
            text (str): 输入文本
            
        Returns:
            List[float]: 对应的嵌入向量列表。如果处理失败，返回随机向量作为占位符。
        """
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception:
            # 返回模拟的嵌入向量（all-MiniLM-L6-v2的维度是384）
            import numpy as np
            return np.random.rand(384).tolist()
    
    def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        基于消息历史进行聊天补全
        
        Args:
            messages (List[Dict[str, str]]): 聊天消息列表，每个消息包含 'role' 和 'content'
            temperature (float): 温度参数，控制响应的随机性，默认为0.7
            
        Returns:
            str: 聊天回复文本。如果出错或服务不可用，返回错误提示信息。
        """
        # 如果启用无Ollama模式，返回模拟响应
        if self.no_ollama_mode:
            # 获取最后一条用户消息
            user_messages = [msg["content"] for msg in messages if msg.get("role") == "user"]
            last_user_message = user_messages[-1] if user_messages else "你好"
            return self._generate_mock_response(last_user_message)
        
        # 检查Ollama连接（快速超时）
        if not self.check_ollama_connection(timeout=1):
            return "⚠️ Ollama服务未启动\n请确保Ollama正在运行，并执行 'ollama serve' 启动服务。"
        
        # 检查模型是否可用
        if not self.check_model_available(timeout=1):
            return f"⚠️ 模型 '{self.model_name}' 未找到\n请执行 'ollama pull {self.model_name}' 下载模型。"
        
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={'temperature': temperature}
            )
            return response['message']['content']
        except Exception as e:
            error_msg = str(e).lower()
            if "not found" in error_msg:
                return f"⚠️ 模型 '{self.model_name}' 未找到\n请执行 'ollama pull {self.model_name}' 下载模型。"
            elif "connection" in error_msg or "refused" in error_msg or "timeout" in error_msg:
                return "⚠️ 无法连接到Ollama服务\n请确保Ollama正在运行。"
            else:
                return f"⚠️ 聊天补全时出错\n{str(e)}"


class MockEmbeddingModel:
    """
    模拟嵌入模型类
    
    用于在真实嵌入模型加载失败时提供占位符功能，避免程序崩溃。
    """
    
    def encode(self, text: str):
        """
        生成模拟的嵌入向量
        
        Args:
            text (str): 输入文本（未被实际使用，仅为了接口兼容）
            
        Returns:
            numpy.ndarray: 长度为384的随机向量
        """
        import numpy as np
        # 返回随机向量作为占位符
        return np.random.rand(384)