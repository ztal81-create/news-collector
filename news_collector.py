import os
import requests
from bs4 import BeautifulSoup

# Настройки
URL = "https://news.ycombinator.com/newest"
HISTORY_FILE = "sent_news.txt"
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f)
    return set()

def save_to_history(link):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")

def send_telegram(message):
    if not BOT_TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }, timeout=10)
    except Exception as e:
        print(f"Ошибка отправки: {e}")

def main():
    sent_links = load_history()
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(URL, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "lxml")
        items = soup.select("tr.athing")

        new_count = 0
        # Проверяем первые 10 свежих записей
        for item in items[:10]:
            link_tag = item.select_one(".titleline > a")
            if not link_tag:
                continue
            
            title = link_tag.text
            link = link_tag['href']

            if link not in sent_links:
                msg = f"<b>🆕 {title}</b>\n\n🔗 {link}"
                send_telegram(msg)
                save_to_history(link)
                new_count += 1
        
        print(f"Найдено новых новостей: {new_count}")

    except Exception as e:
        print(f"Ошибка парсинга: {e}")

if __name__ == "__main__":
    main()
