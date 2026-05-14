#!/usr/bin/env python3
"""
Satellite RAG Assistant - 应用启动脚本

该脚本负责启动Satellite RAG Assistant应用程序，包含以下功能：
- 依赖检查
- 端口可用性检测
- Ollama服务状态检查
- 模型存在性验证
- FastAPI应用启动

Author: Satellite RAG Assistant Team
Date: 2026-05-14
"""

import os
import sys
import socket
import time
from pathlib import Path


def check_port_availability(host: str, port: int) -> bool:
    """
    检查指定主机和端口是否可用
    
    Args:
        host (str): 主机地址
        port (int): 端口号
        
    Returns:
        bool: 如果端口可用返回True，否则返回False
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result != 0
    except Exception:
        return False


def find_available_port(base_port: int, host: str = "127.0.0.1", max_attempts: int = 10) -> int:
    """
    查找可用端口，从base_port开始尝试
    
    Args:
        base_port (int): 起始端口号
        host (str): 主机地址，默认为"127.0.0.1"
        max_attempts (int): 最大尝试次数，默认为10
        
    Returns:
        int: 找到的可用端口号
        
    Raises:
        RuntimeError: 当无法找到可用端口时抛出异常
    """
    for i in range(max_attempts):
        port = base_port + i
        if check_port_availability(host, port):
            return port
    raise RuntimeError(f"无法找到可用端口，已尝试 {base_port} 到 {base_port + max_attempts - 1}")


def check_ollama_service(ollama_host: str) -> tuple[bool, str]:
    """
    检查Ollama服务是否正常运行
    
    Args:
        ollama_host (str): Ollama服务地址
        
    Returns:
        tuple[bool, str]: (服务是否正常, 状态消息)
    """
    try:
        import requests
        response = requests.get(f"{ollama_host}/api/tags", timeout=2)
        if response.status_code == 200:
            return True, "Ollama服务正常运行"
        else:
            return False, f"Ollama服务返回错误状态码: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "无法连接到Ollama服务，请确保Ollama正在运行"
    except requests.exceptions.Timeout:
        return False, "连接Ollama服务超时，请检查服务状态"
    except Exception as e:
        return False, f"检查Ollama服务时发生错误: {str(e)}"


def check_model_exists(ollama_host: str, model_name: str) -> tuple[bool, str]:
    """
    检查指定模型是否已下载并存在于Ollama中
    
    Args:
        ollama_host (str): Ollama服务地址
        model_name (str): 要检查的模型名称
        
    Returns:
        tuple[bool, str]: (模型是否存在, 状态消息)
    """
    try:
        import requests
        response = requests.get(f"{ollama_host}/api/tags", timeout=2)
        if response.status_code == 200:
            models_data = response.json()
            available_models = [model.get('name') for model in models_data.get('models', [])]
            if model_name in available_models:
                return True, f"模型 {model_name} 已存在"
            else:
                return False, f"模型 {model_name} 未找到，请先下载: ollama pull {model_name}"
        else:
            return False, f"无法获取模型列表，状态码: {response.status_code}"
    except Exception as e:
        return False, f"检查模型时发生错误: {str(e)}"


def check_required_dependencies() -> bool:
    """
    检查必需的依赖包是否已安装
    
    Returns:
        bool: 如果所有依赖都已安装返回True，否则返回False
    """
    required_packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("dotenv", "python-dotenv"),
        ("chromadb", "ChromaDB"),
        ("sentence_transformers", "sentence-transformers"),
        ("ollama", "ollama"),
        ("requests", "requests")
    ]
    
    missing_packages = []
    for import_name, display_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(display_name)
    
    if missing_packages:
        print("❌ 缺少必需的依赖包:")
        for pkg in missing_packages:
            print(f"   • {pkg}")
        print("\n💡 请运行以下命令安装依赖:")
        print("   pip install -r requirements.txt")
        return False
    
    return True


def main():
    """
    启动Satellite RAG Assistant应用程序
    
    该函数执行以下步骤：
    1. 检查必需的依赖包
    2. 从配置加载应用参数
    3. 验证Ollama服务状态
    4. 验证指定模型是否存在
    5. 查找可用端口
    6. 启动FastAPI应用
    """
    print("=" * 60)
    print("🚀 Satellite RAG Assistant - 优化启动版")
    print("=" * 60)
    
    # 检查依赖
    if not check_required_dependencies():
        return
    
    # 从环境变量或默认值获取配置
    from app.config import Settings
    settings = Settings()
    
    ollama_host = settings.OLLAMA_HOST
    model_name = settings.LLM_MODEL
    app_host = settings.APP_HOST
    base_port = settings.APP_PORT
    
    print(f"\n📋 当前配置:")
    print(f"   • 大语言模型: {model_name}")
    print(f"   • Ollama地址: {ollama_host}")
    print(f"   • 应用主机: {app_host}")
    print(f"   • 基础端口: {base_port}")
    
    # 检查Ollama服务
    print("\n🔍 检查Ollama服务...")
    ollama_ok, ollama_msg = check_ollama_service(ollama_host)
    if not ollama_ok:
        print(f"❌ {ollama_msg}")
        print("\n💡 解决方案:")
        print("   1. 确保Ollama已安装")
        print("   2. 打开新终端窗口")
        print("   3. 运行命令: ollama serve")
        print("   4. 保持该窗口打开，然后重新运行此脚本")
        return
    
    print(f"✅ {ollama_msg}")
    
    # 检查模型是否存在
    print(f"\n🔍 检查模型 {model_name}...")
    model_exists, model_msg = check_model_exists(ollama_host, model_name)
    if not model_exists:
        print(f"❌ {model_msg}")
        print(f"\n💡 解决方案:")
        print(f"   1. 运行模型下载工具: python download_model.py")
        print(f"   2. 或手动下载: ollama pull {model_name}")
        return
    
    print(f"✅ {model_msg}")
    
    # 查找可用端口
    print(f"\n🔍 查找可用端口...")
    try:
        final_port = find_available_port(base_port, app_host)
        if final_port != base_port:
            print(f"⚠️  端口 {base_port} 被占用，使用端口 {final_port}")
        else:
            print(f"✅ 使用端口 {final_port}")
    except RuntimeError as e:
        print(f"❌ {e}")
        return
    
    # 启动应用
    print(f"\n🚀 启动FastAPI应用...")
    print(f"   主机: {app_host}")
    print(f"   端口: {final_port}")
    print(f"   模型: {model_name}")
    print(f"   访问地址: http://{app_host}:{final_port}")
    print("\n" + "="*60)
    
    try:
        import uvicorn
        uvicorn.run(
            "app.main_final:app",
            host=app_host,
            port=final_port,
            reload=False,
            log_level="info" if settings.DEBUG else "warning"
        )
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("\n💡 可能的解决方案:")
        print("   • 检查端口是否被其他程序占用")
        print("   • 确保所有依赖已正确安装")
        print("   • 检查防火墙设置")


if __name__ == "__main__":
    main()