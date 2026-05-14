#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试提示词管理器功能
"""

import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.prompt_manager import PromptManager

def test_prompt_styles():
    """测试不同风格的提示词"""
    print("=== 测试不同风格的提示词 ===")
    
    # 测试数据
    context = "Landsat-8卫星搭载OLI传感器，全色波段分辨率为15米，多光谱波段分辨率为30米。"
    question = "Landsat-8的空间分辨率是多少？"
    metadata_summary = "Landsat-8技术手册 (第5页)"
    
    styles = ["academic", "engineering", "concise", "remote_sensing", "context"]
    
    for style in styles:
        try:
            if style == "context":
                prompt = PromptManager.get_prompt(
                    style=style,
                    context=context,
                    question=question,
                    metadata_summary=metadata_summary
                )
            else:
                prompt = PromptManager.get_prompt(
                    style=style,
                    context=context,
                    question=question
                )
            print(f"\n--- {style} 风格 ---")
            print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
        except Exception as e:
            print(f"❌ {style} 风格测试失败: {e}")
    
    print("\n=== 测试RAG提示词构建 ===")
    rag_prompt = PromptManager.build_rag_prompt(
        query=question,
        context=context,
        metadata_summary=metadata_summary,
        model_name="qwen2.5:3b",
        style="remote_sensing"
    )
    print("RAG提示词 (前200字符):")
    print(rag_prompt[:200] + "..." if len(rag_prompt) > 200 else rag_prompt)
    
    print("\n=== 测试简单提示词构建 ===")
    simple_prompt = PromptManager.build_simple_prompt(
        query="什么是NDVI指数？",
        file_context="用户上传了植被指数计算文档。",
        model_name="qwen2.5:3b"
    )
    print("简单提示词 (前200字符):")
    print(simple_prompt[:200] + "..." if len(simple_prompt) > 200 else simple_prompt)

def test_dynamic_prompt_generator():
    """测试动态提示词生成器"""
    print("\n=== 测试动态提示词生成器 ===")
    
    generator = DynamicPromptGenerator()
    
    context = "Sentinel-2卫星提供10米、20米和60米三种空间分辨率的数据。"
    question = "Sentinel-2的空间分辨率有哪些？"
    
    complexities = ["low", "medium", "high"]
    
    for complexity in complexities:
        prompt = generator.generate_prompt(
            context=context,
            question=question,
            complexity=complexity,
            include_examples=True,
            include_formatting=True
        )
        print(f"\n--- {complexity} 复杂度 ---")
        print(prompt[:200] + "..." if len(prompt) > 200 else prompt)

def test_all_styles():
    """测试所有可用的提示词风格"""
    print("\n=== 所有可用的提示词风格 ===")
    styles = PromptManager.get_all_styles()
    for key, name in styles.items():
        print(f"{key}: {name}")

if __name__ == "__main__":
    test_all_styles()
    test_prompt_styles()
    test_dynamic_prompt_generator()
    print("\n✅ 所有测试完成！")