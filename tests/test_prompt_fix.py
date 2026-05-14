#!/usr/bin/env python3
"""
测试脚本 - 验证提示词修复是否正常工作
"""

import requests
import json
from app.config import settings
from core.prompt_manager import PromptManager

def test_simple_query():
    """测试简单查询"""
    print("🔍 测试简单查询: '你好'")
    
    # 构建提示词
    prompt = PromptManager.build_rag_prompt(
        query="你好",
        context="无相关文档上下文",
        metadata_summary="无文件来源",
        model_name=settings.LLM_MODEL,
        style="remote_sensing"
    )
    
    print(f"使用的模型: {settings.LLM_MODEL}")
    print(f"提示词长度: {len(prompt)} 字符")
    print("\n提示词预览:")
    print(prompt[:300] + "...")
    
    # 调用Ollama API
    try:
        response = requests.post(
            f"{settings.OLLAMA_HOST}/api/generate",
            json={
                "model": settings.LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 500,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("response", "无法生成回答")
            print(f"\n✅ 模型响应:")
            print(answer)
            return True
        else:
            print(f"\n❌ API调用失败 (状态码: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        return False

def test_with_context():
    """测试带上下文的查询"""
    print("\n" + "="*50)
    print("🔍 测试带上下文查询")
    
    context = "Landsat-8卫星于2013年发射，搭载OLI传感器，提供30米空间分辨率的多光谱影像数据。"
    query = "Landsat-8的空间分辨率是多少？"
    
    prompt = PromptManager.build_rag_prompt(
        query=query,
        context=context,
        metadata_summary="来自Landsat技术文档",
        model_name=settings.LLM_MODEL,
        style="remote_sensing"
    )
    
    print(f"查询: {query}")
    print(f"上下文: {context}")
    
    try:
        response = requests.post(
            f"{settings.OLLAMA_HOST}/api/generate",
            json={
                "model": settings.LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 500,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get("response", "无法生成回答")
            print(f"\n✅ 模型响应:")
            print(answer)
            return True
        else:
            print(f"\n❌ API调用失败 (状态码: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🛰️  Satellite RAG Assistant - 提示词修复测试")
    print("=" * 60)
    
    # 测试Ollama服务
    try:
        ollama_response = requests.get(f"{settings.OLLAMA_HOST}/api/tags", timeout=5)
        if ollama_response.status_code == 200:
            print("✅ Ollama服务正常运行")
        else:
            print("❌ Ollama服务异常")
            return
    except Exception as e:
        print(f"❌ 无法连接到Ollama服务: {e}")
        return
    
    # 执行测试
    test1_success = test_simple_query()
    test2_success = test_with_context()
    
    print("\n" + "="*50)
    if test1_success and test2_success:
        print("🎉 所有测试通过！提示词修复成功！")
    else:
        print("⚠️  部分测试失败，请检查配置")

if __name__ == "__main__":
    main()