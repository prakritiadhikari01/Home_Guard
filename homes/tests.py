from django.test import TestCase

# Create your tests here.
import requests

BASE_URL = "http://127.0.0.1:8000"

session = requests.Session()

# Login
login_data = {
    "username": "admin",
    "password": "admin"
}

login_response = session.post(
    f"{BASE_URL}/admin/login/",
    data=login_data
)

print("Login Status:", login_response.status_code)

# Create Home
payload = {
    "name": "My Smart Home",
    "address": "Kathmandu, Nepal"
}

response = session.post(
    f"{BASE_URL}/api/homes/",
    json=payload
)

print("Create Home Status:", response.status_code)
print(response.text)