import os
import requests, json, sys
sys.stdout.reconfigure(encoding="utf-8")
base = "http://localhost:3000/api"
r = requests.post(base + "/support/user/account/loginByPassword", json={"username": os.environ.get("FASTGPT_USER", "admin"), "password": os.environ.get("FASTGPT_PASSWORD", "1234")}, headers={"Content-Type": "application/json"})
print("Login status:", r.status_code)
print("Response:", r.text[:500])
if r.status_code == 200:
    data = r.json()
    print("Token:", str(data.get("token","none"))[:60])
else:
    for user in ["root", "admin"]:
        r2 = requests.post(base + "/support/user/account/loginByPassword", json={"username": user, "password": os.environ.get("FASTGPT_PASSWORD", "1234")}, headers={"Content-Type": "application/json"})
        print(f"{user}: {r2.status_code} - {r2.text[:200]}")
