import os
import sys

import requests

sys.stdout.reconfigure(encoding="utf-8")
base = "http://localhost:3000/api"
password = os.environ.get("FASTGPT_PASSWORD")
if not password:
    raise SystemExit("Set FASTGPT_PASSWORD to the ADMIN_PASSWORD value from .env")

r = requests.post(base + "/support/user/account/loginByPassword", json={"username": os.environ.get("FASTGPT_USER", "admin"), "password": password}, headers={"Content-Type": "application/json"}, timeout=10)
print("Login status:", r.status_code)
print("Response:", r.text[:500])
if r.status_code == 200:
    print("Login successful")
else:
    for user in ["root", "admin"]:
        r2 = requests.post(base + "/support/user/account/loginByPassword", json={"username": user, "password": password}, headers={"Content-Type": "application/json"}, timeout=10)
        print(f"{user}: {r2.status_code} - {r2.text[:200]}")
