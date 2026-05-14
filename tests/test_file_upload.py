#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细测试文件上传功能
"""

import requests
import os

def test_file_upload():
    """测试文件上传功能"""
    url = "http://127.0.0.1:8002/api/v1/query"
    
    # 创建一个测试文件
    test_content = "这是一个测试文件的内容。Landsat-8卫星的空间分辨率是15米（全色波段）和30米（多光谱波段）。"
    with open("test_file.txt", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    try:
        with open("test_file.txt", "rb") as f:
            files = {"files": ("test_file.txt", f, "text/plain")}
            data = {"query": "这个文件中提到的Landsat-8空间分辨率是多少？"}
            
            response = requests.post(url, data=data, files=files)
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.json()}")
            
    except Exception as e:
        print(f"测试失败: {e}")
    finally:
        # 清理测试文件
        if os.path.exists("test_file.txt"):
            os.remove("test_file.txt")

def test_pure_text():
    """测试纯文字查询"""
    url = "http://127.0.0.1:8002/api/v1/query"
    
    data = {"query": "什么是NDVI指数？"}
    
    try:
        response = requests.post(url, data=data)
        print(f"纯文字查询状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"纯文字查询失败: {e}")

if __name__ == "__main__":
    print("=== 测试纯文字查询 ===")
    test_pure_text()
    
    print("\n=== 测试文件上传查询 ===")
    test_file_upload()
    
    print("\n测试完成！")