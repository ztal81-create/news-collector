import os
import subprocess
import requests
from bs4 import BeautifulSoup

URL = "https://news.ycombinator.com/newest"
HISTORY_FILE = "sent_news.txt"

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def save_history(sent_links):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(sent_links))


def git_commit_history():
    try:
        subprocess.run(["git", "config", "user.name", "news-bot"], check=True)
        subprocess.run(["git", "config", "user.email", "news-bot@github"], check=True)
        subprocess.run(["git", "add", HISTORY_FILE], check=True)
        subprocess.run(["git", "commit", "-m", "Update sent news history"], check=True)
        subprocess.run(["git", "push"], check=True)
    except Exception as e:
        print("Git commit skipped:", e)


def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text[:4000],
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        },
        timeout=10
    )


def main():
    sent_links = load_history()
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(URL, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, "lxml")

    items = soup.select("tr.athing")
    new_links = set(sent_links)
    new_count = 0

    for item in items:
        a = item.select_one(".titleline > a")
        if not a:
            continue

        title = a.get_text(strip=True)
        link = a["href"]

        if link not in sent_links:
            send_telegram(f"🆕 <b>{title}</b>\n🔗 {link}")
            new_links.add(link)
            new_count += 1

    if new_count:
        save_history(new_links)
        git_commit_history()

    print(f"Новых новостей отправлено: {new_count}")


if __name__ == "__main__":
    main()

