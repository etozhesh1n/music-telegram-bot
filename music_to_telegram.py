import os
import json
import time
import requests
from pathlib import Path

# Конфигурация
BOT_TOKEN = "8580527300:AAHVAQmHHkiMSrNZUKsosaP1mTZQ12Ia8nQ"
CHAT_ID = "1783928479"
MUSIC_FILE = r"C:\Users\user\Documents\code\test\my_music.txt"
PROGRESS_FILE = "progress.json"
DOWNLOAD_DIR = "downloads"

# Telegram API
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def load_progress():
    """Загрузить прогресс из файла"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"processed": 0, "sent": [], "failed": []}

def save_progress(progress):
    """Сохранить прогресс в файл"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def send_to_telegram(track_info, audio_url=None):
    """Отправить трек в Telegram"""
    try:
        # Если есть URL аудио, отправляем как аудио
        if audio_url:
            url = f"{TELEGRAM_API}/sendAudio"
            data = {
                "chat_id": CHAT_ID,
                "audio": audio_url,
                "title": track_info.get("title", ""),
                "performer": track_info.get("artist", "")
            }
        else:
            # Если нет URL, отправляем как текст
            url = f"{TELEGRAM_API}/sendMessage"
            text = f"🎵 {track_info['artist']} - {track_info['title']}"
            data = {
                "chat_id": CHAT_ID,
                "text": text
            }

        response = requests.post(url, data=data, timeout=30)
        return response.json().get("ok", False)
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return False

def parse_track_line(line):
    """Парсинг строки трека"""
    line = line.strip()
    if not line:
        return None

    # Убираем номер в начале строки (если есть)
    parts = line.split(maxsplit=1)
    if len(parts) == 2 and parts[0].isdigit():
        line = parts[1]

    # Разделяем по " - "
    if " - " in line:
        artist, title = line.split(" - ", 1)
        return {
            "artist": artist.strip(),
            "title": title.strip(),
            "original": line
        }
    return None

def search_track_youtube(artist, title):
    """Поиск трека на YouTube (заглушка - требует YouTube API)"""
    # Здесь нужно интегрировать YouTube API или yt-dlp
    # Пока возвращаем None
    return None

def main():
    print("🎵 Запуск отправки музыки в Telegram...")
    print(f"📁 Файл: {MUSIC_FILE}")
    print(f"💬 Chat ID: {CHAT_ID}\n")

    # Создаем директорию для загрузок
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Загружаем прогресс
    progress = load_progress()
    start_from = progress["processed"]

    # Читаем файл с треками
    with open(MUSIC_FILE, 'r', encoding='utf-8') as f:
        tracks = f.readlines()

    total = len(tracks)
    print(f"📊 Всего треков: {total}")
    print(f"✅ Уже обработано: {start_from}")
    print(f"⏳ Осталось: {total - start_from}\n")

    if start_from >= total:
        print("✨ Все треки уже отправлены!")
        return

    # Обрабатываем треки
    for i, line in enumerate(tracks[start_from:], start=start_from):
        track_info = parse_track_line(line)

        if not track_info:
            continue

        print(f"[{i+1}/{total}] {track_info['artist']} - {track_info['title']}")

        # Пытаемся найти и отправить трек
        # Пока отправляем как текст (без аудио)
        success = send_to_telegram(track_info)

        if success:
            progress["sent"].append(track_info["original"])
            print("  ✅ Отправлено")
        else:
            progress["failed"].append(track_info["original"])
            print("  ❌ Ошибка")

        progress["processed"] = i + 1
        save_progress(progress)

        # Задержка, чтобы не превысить лимиты Telegram API
        time.sleep(0.5)

        # Каждые 100 треков показываем статистику
        if (i + 1) % 100 == 0:
            print(f"\n📊 Прогресс: {i+1}/{total} ({(i+1)/total*100:.1f}%)")
            print(f"✅ Успешно: {len(progress['sent'])}")
            print(f"❌ Ошибок: {len(progress['failed'])}\n")

    print("\n✨ Готово!")
    print(f"✅ Отправлено: {len(progress['sent'])}")
    print(f"❌ Ошибок: {len(progress['failed'])}")

if __name__ == "__main__":
    main()
