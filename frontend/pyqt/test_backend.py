# Demo Backend Test Script
# Script này giúp test kết nối với backend

import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_backend_connection():
    """Test xem backend có sẵn sàng không"""
    try:
        response = requests.get("http://localhost:5000/")
        if response.status_code == 200:
            print("✅ Backend server đang chạy!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend response code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Không thể kết nối backend: {str(e)}")
        print("💡 Hãy đảm bảo backend đang chạy ở port 5000")
        return False

def test_register():
    """Test API đăng ký"""
    data = {
        "email": "test@example.com",
        "password": "123456",
        "repeatPassword": "123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=data)
        print(f"📝 Register response ({response.status_code}): {response.json()}")
    except Exception as e:
        print(f"❌ Register error: {str(e)}")

def test_login():
    """Test API đăng nhập"""
    data = {
        "email": "test@example.com", 
        "password": "123456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=data)
        result = response.json()
        print(f"🔐 Login response ({response.status_code}): {result}")
        
        if response.status_code == 200 and 'token' in result:
            return result['token']
        return None
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None

def test_file_apis(token):
    """Test file APIs"""
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        # Test get files
        response = requests.get(f"{BASE_URL}/file/list", headers=headers)
        print(f"📁 Get files response ({response.status_code}): {response.json()}")
        
        # Test get keys
        response = requests.get(f"{BASE_URL}/user/get-key", headers=headers)
        print(f"🔑 Get keys response ({response.status_code}): {response.json()}")
        
    except Exception as e:
        print(f"❌ API test error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testing Backend APIs...")
    print("=" * 50)
    
    # Test connection
    if not test_backend_connection():
        print("\n💡 Để chạy backend:")
        print("1. cd backend")
        print("2. npm install")
        print("3. npm run dev")
        exit(1)
    
    print("\n📝 Testing Registration...")
    test_register()
    
    print("\n🔐 Testing Login...")
    token = test_login()
    
    if token:
        print(f"\n🎉 Login thành công! Token: {token[:50]}...")
        print("\n🧪 Testing authenticated APIs...")
        test_file_apis(token)
    else:
        print("\n❌ Login thất bại!")
    
    print("\n✅ Test hoàn thành!")