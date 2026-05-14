#!/usr/bin/env python3
"""
Satellite RAG Assistant - 模型管理工具

该脚本提供Ollama大模型管理功能，包括：
- 列出所有已安装的模型
- 删除不需要的模型
- 清理模型存储空间

Author: Satellite RAG Assistant Team
Date: 2026-05-14
"""

import requests
import json
import sys


def list_models() -> list:
    """
    列出所有已安装的Ollama模型
    
    Returns:
        list: 已安装模型名称列表
        
    Note:
        该函数会显示每个模型的名称和大小信息。
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            if models:
                print("📋 已安装的模型:")
                for i, model in enumerate(models, 1):
                    size_mb = model.get('size', 0) / (1024*1024)
                    print(f"   {i}. {model['name']} ({size_mb:.1f} MB)")
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


def delete_model(model_name: str) -> bool:
    """
    删除指定的Ollama模型
    
    Args:
        model_name (str): 要删除的模型名称
        
    Returns:
        bool: 删除是否成功
    """
    try:
        response = requests.delete(
            "http://localhost:11434/api/delete",
            json={"name": model_name},
            timeout=30
        )
        if response.status_code == 200:
            print(f"✅ 模型 {model_name} 已成功删除")
            return True
        else:
            print(f"❌ 删除失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 删除过程中发生错误: {e}")
        return False


def main():
    """
    模型管理工具主函数
    
    提供交互式界面让用户选择要删除的模型。
    """
    print("=" * 60)
    print("🛰️  Satellite RAG Assistant - 模型删除工具")
    print("=" * 60)
    
    models = list_models()
    if not models:
        print("\n👋 没有可删除的模型")
        return
    
    print(f"\n🗑️  注意: 删除模型将释放磁盘空间，但无法恢复!")
    print("   qwen2.5:3b 是推荐的默认模型，建议保留")
    
    while True:
        choice = input("\n请输入要删除的模型编号 (或输入 'q' 退出): ").strip()
        if choice.lower() == 'q':
            print("👋 退出模型管理工具")
            break
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(models):
                model_to_delete = models[index]
                confirm = input(f"确认删除模型 '{model_to_delete}'? (y/n): ").strip().lower()
                if confirm in ['y', 'yes']:
                    delete_model(model_to_delete)
                    # 刷新模型列表
                    models = list_models()
                    if not models:
                        print("\n👋 所有模型已删除完毕")
                        break
                else:
                    print("❌ 取消删除操作")
            else:
                print("❌ 无效的模型编号")
        except ValueError:
            print("❌ 请输入有效的数字")


if __name__ == "__main__":
    main()