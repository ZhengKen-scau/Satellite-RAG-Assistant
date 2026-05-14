# Satellite RAG Assistant - 环境设置脚本
# 负责设置项目运行所需的环境和目录结构

import os
import shutil
from pathlib import Path

def setup_directories():
    """创建必要的目录结构"""
    directories = [
        "data/raw",
        "data/processed", 
        "data/samples",
        "storage/chroma_db",
        "storage/cache",
        "notebooks"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ 创建目录: {directory}")

def setup_env_file():
    """设置环境变量文件"""
    if not os.path.exists(".env"):
        shutil.copy(".env.example", ".env")
        print("✓ 创建 .env 文件")

def main():
    """主函数"""
    print("设置 Satellite RAG Assistant 环境...")
    setup_directories()
    setup_env_file()
    print("环境设置完成！")

if __name__ == "__main__":
    main()