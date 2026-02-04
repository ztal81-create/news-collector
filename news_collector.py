import os
import requests
from bs4 import BeautifulSoup

# Секреты из GitHub Actions
TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']


def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(
            url,
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text[:4000],
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            },
            timeout=10
        )
    except Exception as e:
        print(f"Telegram error: {e}")


# Загружаем список сайтов
try:
    with open("sites.txt", "r", encoding="utf-8") as f:
        sites = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    send_telegram("❌ Файл sites.txt не найден")
    raise SystemExit


news = []

for url in sites[:5]:  # ограничение для стабильности
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15
        )

        soup = BeautifulSoup(response.text, "lxml")

        headlines = soup.find_all(["h1", "h2", "h3"], limit=3)

        for h in headlines:
            text = h.get_text(strip=True)
            if 20 < len(text) < 150:
                news.append(f"📰 {text}\n🔗 {url}")

    except Exception as e:
        print(f"Error loading {url}: {e}")


if news:
    send_telegram(f"✅ Найдено новостей: {len(news)}")
    for item in news[:5]:
        send_telegram(item)
else:
    send_telegram("Новых новостей нет")

