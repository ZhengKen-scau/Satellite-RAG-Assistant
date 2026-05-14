#!/usr/bin/env python3
"""
Satellite RAG Assistant - 模型管理工具

该脚本提供模型下载和配置管理功能，支持：
- 下载推荐的遥感领域大语言模型
- 配置自定义模型名称
- 自动更新项目配置文件
- 查看系统中所有可用的Ollama模型

Author: Satellite RAG Assistant Team
Date: 2026-05-14
"""

import requests
import json
import sys
import os
from pathlib import Path
from typing import List


def safe_input(prompt: str, default: str = "") -> str:
    """
    安全的输入函数，处理EOF错误和键盘中断
    
    Args:
        prompt (str): 输入提示文本
        default (str): 默认值（可选）
        
    Returns:
        str: 用户输入的字符串，去除首尾空白
        
    Raises:
        SystemExit: 当用户取消操作时退出程序
    """
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        if default:
            print(f"\n使用默认值: {default}")
            return default
        else:
            print("\n👋 操作已取消")
            sys.exit(0)


def validate_model_name(model_name: str) -> tuple[bool, str]:
    """
    验证模型名称是否符合基本格式要求
    
    验证规则：
    - 不能为空
    - 不能包含空格
    - 只能包含字母、数字、冒号(:)、连字符(-)、点(.)和下划线(_)
    - 长度不能超过100个字符
    - 必须包含至少一个字母
    
    Args:
        model_name (str): 要验证的模型名称
        
    Returns:
        tuple[bool, str]: (是否有效, 错误消息或空字符串)
    """
    if not model_name:
        return False, "模型名称不能为空"
    
    # 基本格式检查：不能包含空格、特殊字符限制等
    if ' ' in model_name:
        return False, "模型名称不能包含空格"
    
    if not model_name.replace(':', '').replace('-', '').replace('.', '').replace('_', '').isalnum():
        return False, "模型名称只能包含字母、数字、冒号(:)、连字符(-)、点(.)和下划线(_)"
    
    if len(model_name) > 100:
        return False, "模型名称长度不能超过100个字符"
    
    # 至少需要包含一个字母（避免纯数字名称）
    if not any(c.isalpha() for c in model_name):
        return False, "模型名称必须包含至少一个字母"
    
    return True, ""


def update_env_file(model_name: str) -> None:
    """
    更新.env文件中的LLM_MODEL配置
    
    如果.env文件存在，则更新LLM_MODEL配置；
    如果不存在，则创建新的.env文件并设置必要配置。
    
    Args:
        model_name (str): 要设置的模型名称
    """
    env_path = Path(".env")
    
    if env_path.exists():
        # 读取现有的.env文件
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 更新或添加LLM_MODEL配置
        llm_model_found = False
        new_lines = []
        for line in lines:
            if line.strip().startswith('LLM_MODEL='):
                new_lines.append(f'LLM_MODEL={model_name}\n')
                llm_model_found = True
            else:
                new_lines.append(line)
        
        if not llm_model_found:
            # 如果没有找到LLM_MODEL配置，添加到文件末尾
            new_lines.append(f'\n# 使用{model_name}作为大语言模型\n')
            new_lines.append(f'LLM_MODEL={model_name}\n')
        
        # 写回文件
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        print(f"✅ 已更新 .env 文件，设置 LLM_MODEL={model_name}")
    else:
        # 创建新的.env文件
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write("# Satellite RAG Assistant 配置文件\n")
            f.write(f"LLM_MODEL={model_name}\n")
            f.write("NO_OLLAMA_MODE=false\n")
            f.write("EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2\n")
            f.write("APP_HOST=127.0.0.1\n")
            f.write("APP_PORT=8000\n")
            f.write("DEBUG=false\n")
        
        print(f"✅ 已创建 .env 文件，设置 LLM_MODEL={model_name}")


def get_available_models(ollama_host: str = "http://localhost:11434") -> List[str]:
    """
    获取Ollama中所有可用的模型列表
    
    Args:
        ollama_host (str): Ollama服务地址，默认为"http://localhost:11434"
        
    Returns:
        List[str]: 可用模型名称列表
    """
    try:
        response = requests.get(f"{ollama_host}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            return models
        else:
            return []
    except Exception:
        return []


# 推荐的模型列表（适合遥感领域的专业模型）
"""推荐的遥感领域大语言模型列表，包含模型详细信息"""
RECOMMENDED_MODELS = [
    {
        "name": "qwen2.5:3b",
        "description": "通义千问2.5 3B参数版本（推荐）",
        "size_gb": 1.8,
        "params": "3B",
        "gpu_memory": "6GB+",
        "features": "中文优化，遥感领域表现优秀"
    },
    {
        "name": "llama3.2:3b",
        "description": "Llama 3.2 3B参数版本",
        "size_gb": 1.7,
        "params": "3B", 
        "gpu_memory": "6GB+",
        "features": "多语言支持，通用能力强"
    },
    {
        "name": "phi3:mini",
        "description": "Phi-3 Mini 轻量级模型",
        "size_gb": 1.6,
        "params": "2.7B",
        "gpu_memory": "4GB+",
        "features": "超轻量，适合低配显卡"
    }
]


def download_model(model_name: str) -> bool:
    """
    下载指定的大语言模型
    
    Args:
        model_name (str): 要下载的模型名称
        
    Returns:
        bool: 下载是否成功
        
    Note:
        该函数会显示详细的下载进度，并处理各种异常情况。
    """
    print(f"🚀 正在下载 {model_name} 模型")
    
    # 根据模型名称获取详细信息
    model_info = None
    for model in RECOMMENDED_MODELS:
        if model["name"] == model_name:
            model_info = model
            break
    
    if model_info:
        print(f"   • 推荐模型: {model_info['description']}")
        print(f"   • 大小: ~{model_info['size_gb']}GB | 参数: {model_info['params']} | 显存: {model_info['gpu_memory']}")
        print(f"   • 特点: {model_info['features']}")
    else:
        print(f"   • 自定义模型: {model_name}")
        print(f"   • 大小和参数信息未知")
        print(f"   • 预计下载时间: 5-20分钟 (取决于网络速度和模型大小)")
    
    print("\n📥 开始下载...")
    
    try:
        # 发送下载请求
        response = requests.post(
            "http://localhost:11434/api/pull",
            json={"name": model_name},
            stream=True,
            timeout=300  # 5分钟超时
        )
        
        if response.status_code != 200:
            print(f"❌ 下载请求失败，状态码: {response.status_code}")
            return False
        
        total_size = 0
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    if 'status' in data:
                        status = data['status']
                        if status == "pulling manifest":
                            print("   pulling manifest")
                        elif status == "verifying sha256 digest":
                            print("   verifying sha256 digest")
                        elif status == "writing layer":
                            print("   writing layer")
                        elif status == "removing any unused layers":
                            print("   removing any unused layers")
                        elif status == "success":
                            print("   success")
                        else:
                            print(f"   {status}")
                        
                        # 更新总大小
                        if 'total' in data:
                            total_size = data['total']
                            
                except json.JSONDecodeError:
                    continue
        
        print(f"✅ {model_name} 模型下载完成!")
        if total_size > 0:
            print(f"   总大小: {total_size / (1024*1024):.1f} MB")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Ollama服务")
        print("   请确保Ollama正在运行:")
        print("   1. 打开命令提示符")
        print("   2. 输入: ollama serve")
        print("   3. 保持该窗口打开")
        return False
    except requests.exceptions.Timeout:
        print("❌ 下载超时，请重试")
        return False
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False


def check_existing_models() -> List[str]:
    """
    检查系统中已存在的Ollama模型
    
    Returns:
        List[str]: 已存在模型名称列表
    """
    print("🔍 检查现有模型...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json().get('models', [])
            if models:
                print("📋 已安装的模型:")
                for model in models:
                    size_mb = model.get('size', 0) / (1024*1024)
                    print(f"   • {model['name']} ({size_mb:.1f} MB)")
                return [m['name'] for m in models]
            else:
                print("   暂无已安装模型")
                return []
        else:
            print("   无法获取模型列表")
            return []
    except Exception as e:
        print(f"   检查失败: {e}")
        return []


def show_model_options() -> None:
    """
    显示模型选择选项菜单
    
    该函数打印推荐模型列表和自定义选项，为用户提供清晰的选择界面。
    """
    print("🎯 可用的推荐模型:")
    print()
    for i, model in enumerate(RECOMMENDED_MODELS, 1):
        print(f"{i}. {model['name']}")
        print(f"   描述: {model['description']}")
        print(f"   大小: ~{model['size_gb']}GB | 参数: {model['params']} | 显存: {model['gpu_memory']}")
        print(f"   特点: {model['features']}")
        print()
    
    print("0. 自定义模型名称")
    print("4. 查看系统中所有可用模型")
    print()


def get_user_model_choice() -> str:
    """
    获取用户选择的模型名称
    
    该函数提供交互式模型选择界面，支持：
    - 选择推荐模型（1-3）
    - 输入自定义模型名称（0）
    - 查看所有可用模型（4）
    
    Returns:
        str: 用户选择的模型名称
        
    Raises:
        SystemExit: 当用户取消操作时退出程序
    """
    while True:
        try:
            choice = safe_input("请选择模型 (输入数字 0-4): ")
            if choice == "0":
                # 自定义模型 - 主要用于配置现有模型或指定新模型
                custom_name = safe_input("请输入模型名称 (如: qwen2.5:3b): ")
                is_valid, error_msg = validate_model_name(custom_name)
                if not is_valid:
                    print(f"❌ {error_msg}")
                    continue
                
                # 检查模型是否已存在
                available_models = get_available_models()
                if custom_name in available_models:
                    print(f"✅ 模型 {custom_name} 已存在于系统中")
                    return custom_name
                else:
                    print(f"⚠️  模型 {custom_name} 当前未安装")
                    confirm_download = safe_input("是否现在下载此模型? (y/n): ").lower()
                    if confirm_download in ['y', 'yes', '是']:
                        return custom_name
                    else:
                        print(f"✅ 将使用 {custom_name} 作为配置模型（请确保稍后手动下载）")
                        return custom_name
                        
            elif choice in ["1", "2", "3"]:
                return RECOMMENDED_MODELS[int(choice) - 1]["name"]
            elif choice == "4":
                # 显示所有可用模型
                available_models = get_available_models()
                if available_models:
                    print("\n📋 系统中所有可用的Ollama模型:")
                    for i, model in enumerate(available_models, 1):
                        print(f"   {i}. {model}")
                    print()
                    # 允许用户直接选择现有模型
                    model_choice = safe_input("请输入要使用的模型名称 (或按回车返回): ")
                    if model_choice and model_choice in available_models:
                        return model_choice
                    elif model_choice:
                        print(f"⚠️  {model_choice} 不在可用列表中")
                        confirm_use = safe_input("是否仍要使用此模型名称? (y/n): ").lower()
                        if confirm_use in ['y', 'yes', '是']:
                            return model_choice
                else:
                    print("❌ 无法获取可用模型列表，请确保Ollama服务正在运行")
                continue
            else:
                print("❌ 无效选择，请输入 0-4 之间的数字")
        except KeyboardInterrupt:
            print("\n👋 用户取消操作")
            sys.exit(0)
        except EOFError:
            print("\n❌ 检测到非交互式环境，使用默认模型: qwen2.5:3b")
            return "qwen2.5:3b"
        except Exception as e:
            print(f"❌ 输入错误: {e}")
            print("❌ 使用默认模型: qwen2.5:3b")
            return "qwen2.5:3b"


def main() -> None:
    """
    模型管理工具主函数
    
    该函数执行以下步骤：
    1. 检查系统中已存在的模型
    2. 显示默认模型状态
    3. 询问用户是否要配置/下载模型
    4. 提供模型选择界面
    5. 处理用户选择并执行相应操作
    6. 自动更新项目配置文件
    """
    print("=" * 60)
    print("🛰️  Satellite RAG Assistant - 模型管理工具")
    print("=" * 60)
    print()
    
    # 检查现有模型
    existing_models = check_existing_models()
    default_model = "qwen2.5:3b"
    
    if default_model in existing_models:
        print(f"\n✅ {default_model} 模型已安装，无需重新下载")
        print("   你可以直接运行应用: python run_simple.py")
    else:
        print(f"\n⚠️  {default_model} 模型未安装")
    
    # 询问是否要配置模型
    configure_model = safe_input("\n是否要配置/下载模型? (y/n): ").lower()
    if configure_model not in ['y', 'yes', '是']:
        print("👋 退出模型管理工具")
        return
    
    # 显示模型选项并获取用户选择
    show_model_options()
    selected_model = get_user_model_choice()
    
    # 检查模型是否已存在
    available_models = get_available_models()
    if selected_model in available_models:
        print(f"\n✅ 模型 {selected_model} 已存在")
        # 直接更新配置
        update_env_file(selected_model)
        print(f"\n🎉 配置完成!")
        print(f"   现在可以启动应用了:")
        print(f"   python run_simple.py")
        print(f"\n🌐 访问地址: http://127.0.0.1:8000")
        return
    else:
        # 下载模型
        success = download_model(selected_model)
        if success:
            # 更新.env文件
            update_env_file(selected_model)
            print(f"\n🎉 准备就绪!")
            print(f"   现在可以启动应用了:")
            print(f"   python run_simple.py")
            print(f"\n🌐 访问地址: http://127.0.0.1:8000")
        else:
            print("❌ 模型下载失败")
            # 即使下载失败，也更新配置（用户可能手动下载）
            update_env_file(selected_model)
            print(f"✅ 已更新配置为 {selected_model}")
            print("💡 请手动下载模型后启动应用")


if __name__ == "__main__":
    main()
