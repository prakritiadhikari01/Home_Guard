import requests
import base64

with open("abc.jpeg", "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode()

res = requests.post(
    "http://192.168.1.6:8001/analyze",
    json={"image": img_base64}
)

print(res.json())