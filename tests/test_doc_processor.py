#!/usr/bin/env python3

from core.document_processor import DocumentProcessor
import tempfile
import os

def test_doc_processor():
    dp = DocumentProcessor()
    
    with tempfile.TemporaryDirectory() as tmp:
        test_file = os.path.join(tmp, 'test.doc')
        # 创建一个空的DOC文件
        with open(test_file, 'wb') as f:
            f.write(b'\x00' * 100)  # 写入一些二进制数据
        
        try:
            result = dp.process_documents([test_file])
            print(f"Success: processed {len(result)} documents")
            if result:
                print(f"Content: {result[0]['content']}")
                print(f"Metadata: {result[0]['metadata']}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_doc_processor()