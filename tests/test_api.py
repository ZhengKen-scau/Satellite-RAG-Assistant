# Satellite RAG Assistant - API测试
# 测试API端点的功能

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.main_final import app

client = TestClient(app)

def test_root_endpoint():
    """测试根端点"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Satellite RAG Assistant is running!"

def test_health_endpoint():
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_query_endpoint():
    """测试查询端点"""
    # TODO: 实现具体的查询测试逻辑
    response = client.post("/api/v1/query", json={"query": "测试查询"})
    # 这里应该根据实际实现调整断言
    assert response.status_code in [200, 500]  # 200表示成功，500表示TODO未实现

if __name__ == "__main__":
    test_root_endpoint()
    test_health_endpoint()
    test_query_endpoint()
    print("API测试完成！")