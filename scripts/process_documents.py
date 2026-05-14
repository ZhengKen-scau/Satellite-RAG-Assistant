# Satellite RAG Assistant - 文档处理脚本
# 负责处理原始文档并创建向量数据库

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from core.document_processor import DocumentProcessor
from core.vector_store import VectorStoreManager

def process_documents():
    """处理文档并创建向量存储"""
    print("开始处理文档...")
    
    # 初始化文档处理器
    processor = DocumentProcessor()
    
    # 处理原始文档
    processed_docs = processor.process_directory("data/raw", "data/processed")
    print(f"✓ 处理完成 {len(processed_docs)} 个文档块")
    
    # 创建向量存储
    vector_store = VectorStoreManager()
    vector_store.add_documents(processed_docs)
    print("✓ 向量数据库创建完成")

def main():
    """主函数"""
    print("Satellite RAG Assistant - 文档处理脚本")
    process_documents()
    print("文档处理完成！")

if __name__ == "__main__":
    main()