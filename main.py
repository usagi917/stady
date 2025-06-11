import random

運勢 = random.randint(1, 100)
print(f"今日の運勢は...{運勢}点！")

if 運勢 >= 80:
    print("🌟 大吉！素晴らしい一日になりそう！")
elif 運勢 >= 60:
    print("😊 中吉！良いことがありそう")
elif 運勢 >= 40:
    print("🍀 小吉！ちょっとラッキー")
else:
    print("💪 今日は自分で運を作る日！")
