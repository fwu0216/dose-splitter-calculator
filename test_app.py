#!/usr/bin/env python3
"""
放射性药物分装计算器测试脚本
"""

import requests
import json
import time

BASE_URL = "http://localhost:5001"

def test_health_check():
    """测试健康检查端点"""
    print("测试健康检查...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✓ 健康检查通过")

def test_nuclides_api():
    """测试核素信息API"""
    print("测试核素信息API...")
    response = requests.get(f"{BASE_URL}/api/nuclides")
    assert response.status_code == 200
    data = response.json()
    assert "F18" in data["nuclides"]
    assert "C11" in data["nuclides"]
    assert data["half_lives"]["F18"] == 109.7
    assert data["half_lives"]["C11"] == 20.3
    print("✓ 核素信息API通过")

def test_current_time_api():
    """测试当前时间API"""
    print("测试当前时间API...")
    response = requests.get(f"{BASE_URL}/api/current-time")
    assert response.status_code == 200
    data = response.json()
    assert "current_time" in data
    assert "timezone" in data
    assert data["timezone"] == "Asia/Shanghai"
    print("✓ 当前时间API通过")

def test_calculation_api():
    """测试计算API"""
    print("测试计算API...")
    
    # 测试F-18计算
    test_data = {
        "nuclide": "F18",
        "init_time": "07:00",
        "target_time": "07:30",
        "init_activity": "178.8",
        "init_volume": "10",
        "desired_dose": "7.56"
    }
    
    response = requests.post(f"{BASE_URL}/api/calculate", 
                           json=test_data,
                           headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "result" in data
    assert "required_volume" in data["result"]
    assert "current_activity" in data["result"]
    assert "current_concentration" in data["result"]
    
    # 验证计算结果
    result = data["result"]
    assert abs(result["current_activity"] - 147.93) < 0.1
    assert abs(result["current_concentration"] - 14.793) < 0.01
    assert abs(result["required_volume"] - 0.511) < 0.001
    assert result["elapsed_minutes"] == 30.0
    
    print("✓ 计算API通过")

def test_c11_calculation():
    """测试C-11计算"""
    print("测试C-11计算...")
    
    test_data = {
        "nuclide": "C11",
        "init_time": "08:00",
        "target_time": "08:20",
        "init_activity": "50.0",
        "init_volume": "5",
        "desired_dose": "10.0"
    }
    
    response = requests.post(f"{BASE_URL}/api/calculate", 
                           json=test_data,
                           headers={"Content-Type": "application/json"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    
    result = data["result"]
    # C-11半衰期20.3分钟，20分钟后活度应该约为初始活度的一半
    expected_activity = 50.0 * (0.5 ** (20 / 20.3))
    assert abs(result["current_activity"] - expected_activity) < 1.0
    
    print("✓ C-11计算通过")

def test_saved_data_api():
    """测试保存数据API"""
    print("测试保存数据API...")
    response = requests.get(f"{BASE_URL}/api/saved-data")
    assert response.status_code == 200
    data = response.json()
    # 应该返回一个字典（可能是空的）
    assert isinstance(data, dict)
    print("✓ 保存数据API通过")

def test_main_page():
    """测试主页面"""
    print("测试主页面...")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "放射性药物分装计算器" in response.text
    assert "选择核素" in response.text
    assert "初始数据" in response.text
    print("✓ 主页面通过")

def test_error_handling():
    """测试错误处理"""
    print("测试错误处理...")
    
    # 测试无效数据
    invalid_data = {
        "nuclide": "INVALID",
        "init_time": "invalid",
        "target_time": "invalid",
        "init_activity": "not_a_number",
        "init_volume": "not_a_number",
        "desired_dose": "not_a_number"
    }
    
    response = requests.post(f"{BASE_URL}/api/calculate", 
                           json=invalid_data,
                           headers={"Content-Type": "application/json"})
    assert response.status_code == 400
    data = response.json()
    assert data["success"] == False
    assert "error" in data
    
    print("✓ 错误处理通过")

def main():
    """运行所有测试"""
    print("开始测试放射性药物分装计算器...")
    print("=" * 50)
    
    try:
        test_health_check()
        test_nuclides_api()
        test_current_time_api()
        test_calculation_api()
        test_c11_calculation()
        test_saved_data_api()
        test_main_page()
        test_error_handling()
        
        print("=" * 50)
        print("🎉 所有测试通过！应用运行正常。")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
