#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的API功能
"""

import requests

def test_pure_text_query():
    """测试纯文字查询"""
    url = "http://127.0.0.1:8002/api/v1/query"
    
    # 测试纯文字消息
    data = {"query": "你好，这是一个测试消息"}
    
    try:
        response = requests.post(url, data=data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return True
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def test_with_file_query():
    """测试带文件的查询（模拟）"""
    url = "http://127.0.0.1:8002/api/v1/query"
    
    data = {"query": "基于上传的文件回答问题"}
    
    try:
        response = requests.post(url, data=data)
        print(f"带文件查询状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return True
    except Exception as e:
        print(f"带文件查询测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=== 测试纯文字查询 ===")
    test_pure_text_query()
    
    print("\n=== 测试带文件查询 ===")
    test_with_file_query()
    
    print("\n测试完成！")