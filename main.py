import time

print("ロケット発射まで...")
for i in range(5, 0, -1):
    print(f"{i}...")
    time.sleep(0)  # 1秒待つ
print("🚀 発射！！！")
