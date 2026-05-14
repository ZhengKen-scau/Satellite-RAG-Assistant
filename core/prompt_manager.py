# Satellite RAG Assistant - 提示词管理器
# 负责管理和提供不同风格的提示词模板

import os
from typing import List, Dict, Any  # 添加List导入

class PromptManager:
    """卫星遥感RAG系统提示词管理器（简化版）"""
    
    # 针对遥感领域的专业提示词（最终优化版本）
    REMOTE_SENSING_PROMPT = """你是一位专业的卫星遥感数据分析专家。请严格按照以下要求回答问题：

## 语言要求
- 必须使用简体中文回答
- 绝对禁止使用英文或其他语言

## 回答原则
1. **基于可用信息回答**：如果上下文包含具体的技术信息、数据或内容，请直接引用
2. **诚实承认未知**：如果上下文只包含文件基本信息（如"Word文档已上传"），请基于文件类型和名称提供一般性建议
3. **禁止编造信息**：不要添加上下文中不存在的具体技术细节或数据
4. **提供有用指导**：即使无法回答具体内容，也要给出相关的使用建议或后续步骤

## 上下文信息
{context}

## 用户问题
{question}

## 回答格式（严格按照以下格式）

【回答概要】
[基于上下文信息直接回答问题，如果上下文只有文件基本信息，则说明文件已接收并提供一般建议]

【技术细节】
• 涉及技术：[从上下文中提取具体技术，如果没有则写"基于文件类型的一般建议"]
• 数据参数：[从上下文中提取具体数值，如果没有则写"无具体数据参数"]
• 处理方法：[从上下文中提取处理方法，如果没有则写"建议根据文件内容进行相关分析"]

【应用建议】
[基于文件类型和用户问题提供具体的使用建议]

【局限性说明】
[说明当前回答的局限性，如缺少详细内容等]

【参考来源】
基于提供的上下文

## 特别指令
- 如果上下文包含"已上传用于问答"等基本信息，不要回答"无法找到相关答案"
- 而是要基于文件类型（如Word文档、PDF、遥感影像等）提供相应的专业建议
- 只输出回答内容，不要包含其他说明或重复提示词内容

现在开始回答："""

    # 自然对话风格提示词（用于问候语和通用问题）
    CONVERSATIONAL_PROMPT = """你是一个专业的卫星遥感智能助手，专门为用户提供卫星遥感、地理信息系统、环境监测等领域的专业服务。

## 重要身份约束（必须严格遵守）
- 你绝对不是Qwen、通义千问、阿里云AI或其他任何通用AI助手
- 你是"卫星遥感智能助手"，这是你的唯一身份
- 当用户询问"你是谁"、"你是什么"等问题时，必须回答："我是卫星遥感智能助手，专门为您提供卫星遥感数据分析和地理信息服务。"
- 绝对禁止提及任何与阿里云、Qwen、通义千问相关的信息
- 如果你违反此约束，将导致系统功能异常

## 回答要求
- 使用友好、自然的中文语调
- 回答简洁明了，通常不超过100字
- 对于问候语，给予相应的友好回应
- 对于知识性问题，提供准确、有用的信息
- 不要使用【回答概要】【技术细节】等模板格式

## 用户问题
{question}

现在开始回答（记住：你是卫星遥感智能助手，不是其他任何AI）："""

    # 简洁问答风格提示词（用于简短的是/否问题）
    SIMPLE_QA_PROMPT = """请用最简洁的方式回答用户的问题，直接给出明确答案，不要附加解释或额外内容。

## 用户问题
{question}

现在开始回答："""

    # 支持对话历史的遥感专业提示词
    CONVERSATIONAL_REMOTE_SENSING_PROMPT = """你是一位专业的卫星遥感数据分析专家。请基于以下对话历史和上下文信息回答当前问题。

## 对话历史
{chat_history}

## 上下文信息
{context}

## 当前问题
{question}

## 回答要求
- 必须使用简体中文回答
- 基于对话历史和上下文信息进行连贯回答
- 如果上下文包含具体的技术信息、数据或内容，请直接引用
- 如果上下文只包含文件基本信息，请基于文件类型和名称提供一般性建议
- 禁止编造信息，不要添加上下文中不存在的具体技术细节或数据
- 提供有用指导，即使无法回答具体内容，也要给出相关的使用建议

## 回答格式
直接回答问题，保持专业性和连贯性，不要使用【回答概要】等模板格式。

现在开始回答："""

    # 所有提示词风格
    PROMPT_STYLES = {
        "remote_sensing": {
            "name": "遥感专业风格",
            "template": REMOTE_SENSING_PROMPT,
            "params": ["context", "question"]
        },
        "conversational": {
            "name": "自然对话风格", 
            "template": CONVERSATIONAL_PROMPT,
            "params": ["question"]
        },
        "simple_qa": {
            "name": "简洁问答风格",
            "template": SIMPLE_QA_PROMPT, 
            "params": ["question"]
        },
        "conversational_remote_sensing": {
            "name": "对话式遥感专业风格",
            "template": CONVERSATIONAL_REMOTE_SENSING_PROMPT,
            "params": ["chat_history", "context", "question"]
        }
    }
    
    @staticmethod
    def _is_basic_context(context: str) -> bool:
        """
        判断上下文是否只包含基本信息（如文件上传提示等）
        """
        if not context.strip():
            return True
            
        basic_indicators = [
            "已上传",
            "用于问答", 
            "可用于问答",
            "基本信息",
            "Word文档",
            "PDF文件",
            "文件已上传",
            "支持格式"
        ]
        
        # 如果上下文很短（少于50个字符）且包含基本信息指示词，则认为是基本信息
        if len(context) < 50:
            for indicator in basic_indicators:
                if indicator in context:
                    return True
                    
        return False
    
    @classmethod
    def detect_style(cls, query: str, context: str = "", chat_history: List[dict] = None) -> str:
        """
        根据问题类型、上下文和对话历史自动选择合适的回复风格
        
        Args:
            query: 用户查询
            context: 检索到的上下文
            chat_history: 对话历史
            
        Returns:
            选择的风格名称
        """
        # 如果有对话历史，优先使用对话式风格
        if chat_history and len(chat_history) > 0:
            # 如果存在有效文档上下文且问题与之相关，使用对话式遥感专业风格
            if context and context.strip() and not cls._is_basic_context(context):
                return "conversational_remote_sensing"
            else:
                return "conversational"
        
        # 如果存在有效文档上下文且问题与之相关，使用遥感专业风格
        if context and context.strip() and not cls._is_basic_context(context):
            return "remote_sensing"
        
        # 检测问候语
        greetings = ["你好", "嗨", "hello", "hi", "早上好", "下午好", "晚上好", "在吗"]
        for greeting in greetings:
            if greeting in query:
                return "conversational"
                
        # 检测知识型提问模式
        knowledge_patterns = ["什么是", "如何", "解释一下", "介绍一下", "为什么", "怎么"]
        for pattern in knowledge_patterns:
            if pattern in query:
                return "conversational"
                
        # 检测简短的是/否类问题
        if len(query.strip()) <= 20:
            yes_no_indicators = ["是", "否", "对", "错", "可以", "行", "能", "会", "?", "？"]
            for indicator in yes_no_indicators:
                if indicator in query:
                    return "simple_qa"
                    
        # 默认使用自然对话风格
        return "conversational"
    
    @classmethod
    def format_chat_history(cls, chat_history: List[dict]) -> str:
        """格式化对话历史为字符串"""
        if not chat_history:
            return "无对话历史"
            
        formatted_history = []
        for msg in chat_history:
            role = "用户" if msg.get("role") == "user" else "助手"
            content = msg.get("content", "")
            formatted_history.append(f"{role}: {content}")
            
        return "\n".join(formatted_history)
    
    @classmethod
    def build_rag_prompt(cls, query: str, context: str, metadata_summary: str = "", 
                        model_name: str = "qwen2.5:3b", style: str = None, 
                        chat_history: List[dict] = None) -> str:
        """构建RAG查询提示词（支持多风格自动切换和对话历史）
        
        Args:
            query: 用户查询
            context: 检索到的上下文
            metadata_summary: 元数据摘要（保留参数但不使用）
            model_name: 模型名称（保留参数但不使用）
            style: 提示词风格（如果为None，则自动检测）
            chat_history: 对话历史
            
        Returns:
            完整的提示词字符串
        """
        # 如果未指定风格，自动检测
        if style is None:
            style = cls.detect_style(query, context, chat_history)
            
        # 准备参数
        if style == "remote_sensing":
            template = cls.REMOTE_SENSING_PROMPT
            formatted_template = template.replace("{{", "{").replace("}}", "}")
            return formatted_template.format(context=context, question=query)
        elif style == "conversational_remote_sensing":
            template = cls.CONVERSATIONAL_REMOTE_SENSING_PROMPT
            formatted_template = template.replace("{{", "{").replace("}}", "}")
            return formatted_template.format(
                chat_history=cls.format_chat_history(chat_history),
                context=context,
                question=query
            )
        elif style == "conversational":
            template = cls.CONVERSATIONAL_PROMPT
            formatted_template = template.replace("{{", "{").replace("}}", "}")
            return formatted_template.format(question=query)
        elif style == "simple_qa":
            template = cls.SIMPLE_QA_PROMPT
            formatted_template = template.replace("{{", "{").replace("}}", "}")
            return formatted_template.format(question=query)
        else:
            # 默认使用自然对话风格
            template = cls.CONVERSATIONAL_PROMPT
            formatted_template = template.replace("{{", "{").replace("}}", "}")
            return formatted_template.format(question=query)

    @classmethod
    def build_simple_prompt(cls, query: str, file_context: str = "", 
                           model_name: str = "qwen2.5:3b", chat_history: List[dict] = None) -> str:
        """构建简单查询提示词（用于无RAG的情况，支持多风格和对话历史）"""
        # 自动检测风格
        style = cls.detect_style(query, file_context, chat_history)
        
        if file_context:
            context = f"用户上传的文件信息：\n{file_context}"
        else:
            context = "无相关文档上下文"
            
        if style == "remote_sensing":
            template = cls.REMOTE_SENSING_PROMPT
            formatted_template = template.replace("{{", "{").replace("}}", "}")
            return formatted_template.format(context=context, question=query)
        elif style == "conversational_remote_sensing":
            template = cls.CONVERSATIONAL_REMOTE_SENSING_PROMPT
            formatted_template = template.replace("{{", "{").replace("}}", "}")
            return formatted_template.format(
                chat_history=cls.format_chat_history(chat_history),
                context=context,
                question=query
            )
        elif style == "conversational":
            template = cls.CONVERSATIONAL_PROMPT
            formatted_template = template.replace("{{", "{").replace("}}", "}")
            return formatted_template.format(question=query)
        elif style == "simple_qa":
            template = cls.SIMPLE_QA_PROMPT
            formatted_template = template.replace("{{", "{").replace("}}", "}")
            return formatted_template.format(question=query)
        else:
            # 默认使用自然对话风格
            template = cls.CONVERSATIONAL_PROMPT
            formatted_template = template.replace("{{", "{").replace("}}", "}")
            return formatted_template.format(question=query)