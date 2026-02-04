import os
import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={
            'chat_id': TELEGRAM_CHAT_ID,
            'text': text[:4000],
            'parse_mode': 'HTML',
            'disable_web_page_preview': 'False'
        }, timeout=10)
    except Exception as e:
        print(f"Ошибка: {e}")

# Проверяем, есть ли файл с сайтами
try:
    with open('sites.txt', 'r', encoding='utf-8') as f:
        sites = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    send_telegram("❌ Файл sites.txt не найден!")
    exit()

new_items = []

for url in sites[:5]:
    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        soup = BeautifulSoup(resp.text, 'lxml')
        
        # Ищем заголовки
        headlines = soup.find_all(['h1', 'h2', 'h3'], limit=3)
        
        for el in headlines:
            text = el.get_text(strip=True)
            if 20 < len(text) < 150:
                new_items.append(f"📰 {text}\n🔗 {url}")
    except Exception as e:
        print(f"Ошибка: {e}")

if new_items:
    send_telegram(f"✅ Найдено: {len(new_items)} новостей")
    for item in new_items[:5]:
        send_telegram(item)
else:
    send_telegram("Новых новостей нет")
