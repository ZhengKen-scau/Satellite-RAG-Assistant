#!/usr/bin/env python3
"""
测试脚本 - 验证优化后的遥感专业提示词效果
"""

import requests
import json
from app.config import settings
from core.prompt_manager import PromptManager

def test_simple_chinese_query():
    """测试简单中文查询"""
    print("🔍 测试简单中文查询: '你好，能介绍一下卫星遥感吗？'")
    
    # 构建提示词
    prompt = PromptManager.build_rag_prompt(
        query="你好，能介绍一下卫星遥感吗？",
        context="无相关文档上下文"
    )
    
    print(f"使用的模型: {settings.LLM_MODEL}")
    print(f"提示词长度: {len(prompt)} 字符")
    print("\n提示词预览:")
    print(prompt[:400] + "...")
    
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
                    "num_predict": 800,
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
            
            # 检查是否包含中文和正确格式
            if "【回答概要】" in answer and any(char.isalpha() and ord(char) > 127 for char in answer):
                print("✅ 回答包含中文和正确格式")
                return True
            else:
                print("❌ 回答格式或语言不符合要求")
                return False
        else:
            print(f"\n❌ API调用失败 (状态码: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        return False

def test_document_based_query():
    """测试基于文档的查询"""
    print("\n" + "="*60)
    print("🔍 测试基于文档的查询")
    
    context = """Landsat-8卫星于2013年2月11日发射，搭载了两个主要传感器：
1. OLI (Operational Land Imager) - 运行土地成像仪
2. TIRS (Thermal Infrared Sensor) - 热红外传感器

OLI提供9个光谱波段，空间分辨率为30米（全色波段为15米）。
TIRS提供2个热红外波段，空间分辨率为100米。

重访周期为16天，数据免费开放。"""
    
    query = "Landsat-8的空间分辨率是多少？"
    
    prompt = PromptManager.build_rag_prompt(
        query=query,
        context=context
    )
    
    print(f"查询: {query}")
    print(f"上下文长度: {len(context)} 字符")
    
    try:
        response = requests.post(
            f"{settings.OLLAMA_HOST}/api/generate",
            json={
                "model": settings.LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 800,
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
            
            # 检查是否正确引用了文档信息
            if "30米" in answer and "15米" in answer and "100米" in answer:
                print("✅ 正确引用了文档中的具体数据")
                return True
            else:
                print("⚠️  可能没有充分利用文档信息")
                return False
        else:
            print(f"\n❌ API调用失败 (状态码: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        return False

def test_no_context_query():
    """测试无上下文时的诚实回答"""
    print("\n" + "="*60)
    print("🔍 测试无上下文时的诚实回答")
    
    context = "无相关文档上下文"
    query = "Sentinel-3卫星的详细技术参数是什么？"
    
    prompt = PromptManager.build_rag_prompt(
        query=query,
        context=context
    )
    
    print(f"查询: {query}")
    print("上下文: 无相关文档上下文")
    
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
            
            # 检查是否诚实承认不知道
            if "无法找到相关答案" in answer or "不知道" in answer or "没有相关信息" in answer:
                print("✅ 诚实承认不知道，符合要求")
                return True
            else:
                print("⚠️  可能编造了不存在的信息")
                return False
        else:
            print(f"\n❌ API调用失败 (状态码: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 70)
    print("🛰️  Satellite RAG Assistant - 优化提示词测试")
    print("=" * 70)
    
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
    test1_success = test_simple_chinese_query()
    test2_success = test_document_based_query()
    test3_success = test_no_context_query()
    
    print("\n" + "="*70)
    if test1_success and test2_success and test3_success:
        print("🎉 所有测试通过！优化后的提示词效果优秀！")
        print("\n🌟 优化效果总结:")
        print("✅ 统一使用遥感专业风格提示词")
        print("✅ 强制中文回答，杜绝英文输出")
        print("✅ 基于文档内容提供针对性回答")
        print("✅ 无上下文时诚实承认不知道")
        print("✅ 保持专业格式：【回答概要】【技术细节】等")
    else:
        print("⚠️  部分测试未完全通过，请检查提示词配置")

if __name__ == "__main__":
    main()