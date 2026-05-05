import os
import time
import requests
import yt_dlp
import sys

# Исправление кодировки для Windows консоли
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Конфигурация
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8580527300:AAHVAQmHHkiMSrNZUKsosaP1mTZQ12Ia8nQ")
DOWNLOAD_DIR = "downloads"

# Список разрешенных пользователей (пустой = все могут использовать)
ALLOWED_USERS = os.environ.get("ALLOWED_USERS", "").split(",") if os.environ.get("ALLOWED_USERS") else []

# Telegram API
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    """Отправить текстовое сообщение"""
    try:
        url = f"{TELEGRAM_API}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        response = requests.post(url, data=data, timeout=30)
        return response.json().get("ok", False)
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")
        return False

def send_audio(chat_id, file_path, artist, title):
    """Отправить аудиофайл"""
    try:
        url = f"{TELEGRAM_API}/sendAudio"
        with open(file_path, 'rb') as audio_file:
            files = {'audio': audio_file}
            data = {
                'chat_id': chat_id,
                'performer': artist,
                'title': title
            }
            response = requests.post(url, data=data, files=files, timeout=120)
            return response.json().get('ok', False)
    except Exception as e:
        print(f"Ошибка отправки аудио: {e}")
        return False

def download_from_youtube(query, output_path):
    """Скачать аудио с YouTube"""
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'skip': ['hls', 'dash', 'translated_subs']
                }
            },
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_query = f"ytsearch1:{query}"
            info = ydl.extract_info(search_query, download=True)

            if info and 'entries' in info and len(info['entries']) > 0:
                return True
            return False
    except Exception as e:
        print(f"Ошибка скачивания: {e}")
        return False

def parse_track(text):
    """Парсинг названия трека из текста"""
    text = text.strip()

    # Убираем команды бота
    if text.startswith('/'):
        return None

    # Если есть " - ", разделяем на исполнителя и название
    if " - " in text:
        parts = text.split(" - ", 1)
        artist = parts[0].strip()
        title = parts[1].strip()

        # Убираем лишние приписки типа "feat.", "(Official Audio)", "[Lyrics]" и т.д.
        # Оставляем только основное название
        for suffix in [" (Official", " [Official", " (Lyric", " [Lyric", " (Audio", " [Audio",
                       " (Music Video", " [Music Video", " (Official Music Video", " - Topic"]:
            if suffix.lower() in title.lower():
                title = title[:title.lower().index(suffix.lower())].strip()

        return {"artist": artist, "title": title, "query": f"{artist} {title}"}
    else:
        # Если нет " - ", считаем что это просто название трека
        # Убираем приписки
        clean_text = text
        for suffix in [" (Official", " [Official", " (Lyric", " [Lyric", " (Audio", " [Audio",
                       " (Music Video", " [Music Video", " (Official Music Video"]:
            if suffix.lower() in clean_text.lower():
                clean_text = clean_text[:clean_text.lower().index(suffix.lower())].strip()

        return {"artist": "Unknown Artist", "title": clean_text, "query": clean_text}

def get_updates(offset=None):
    """Получить обновления от Telegram"""
    try:
        url = f"{TELEGRAM_API}/getUpdates"
        params = {"timeout": 30, "offset": offset}
        response = requests.get(url, params=params, timeout=35)
        return response.json()
    except Exception as e:
        print(f"Ошибка получения обновлений: {e}")
        return None

def process_track(chat_id, track_info):
    """Обработать запрос на скачивание трека"""
    artist = track_info['artist']
    title = track_info['title']
    query = track_info['query']

    print(f"\n🎵 Запрос: {artist} - {title}")
    send_message(chat_id, f"🔍 Ищу: {artist} - {title}")

    # Создаем безопасное имя файла
    safe_filename = f"{artist}_{title}"[:100]
    safe_filename = "".join(c for c in safe_filename if c.isalnum() or c in (' ', '-', '_')).strip()
    output_file = os.path.join(DOWNLOAD_DIR, safe_filename)

    # Скачиваем
    if download_from_youtube(query, output_file):
        mp3_file = output_file + '.mp3'

        if os.path.exists(mp3_file):
            file_size = os.path.getsize(mp3_file) / (1024 * 1024)
            print(f"✅ Скачано ({file_size:.1f} MB)")
            send_message(chat_id, f"✅ Скачано! Отправляю...")

            # Отправляем
            if send_audio(chat_id, mp3_file, artist, title):
                print(f"✅ Отправлено")
                # Удаляем файл
                try:
                    os.remove(mp3_file)
                except:
                    pass
            else:
                send_message(chat_id, "❌ Ошибка отправки")
        else:
            send_message(chat_id, "❌ Файл не найден после скачивания")
    else:
        send_message(chat_id, f"❌ Не удалось найти: {query}")

def main():
    print("🤖 Бот запущен и ожидает сообщений...")
    print("📝 Отправьте боту название трека в формате:")
    print("   - 'Исполнитель - Название'")
    print("   - или просто 'Название трека'\n")

    # Создаем директорию для загрузок
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    offset = None

    while True:
        try:
            # Получаем обновления
            updates = get_updates(offset)

            if updates and updates.get('ok'):
                for update in updates.get('result', []):
                    offset = update['update_id'] + 1

                    # Проверяем наличие сообщения
                    if 'message' not in update:
                        continue

                    message = update['message']
                    chat_id = message['chat']['id']

                    # Проверка разрешенных пользователей (если список не пустой)
                    if ALLOWED_USERS and str(chat_id) not in ALLOWED_USERS:
                        send_message(chat_id, "❌ У вас нет доступа к этому боту")
                        continue

                    # Обрабатываем только текстовые сообщения
                    if 'text' not in message:
                        continue

                    text = message['text']

                    # Команда /start
                    if text == '/start':
                        send_message(chat_id, "👋 Привет! Отправь мне название трека, и я скачаю его для тебя!\n\nФормат:\n• Исполнитель - Название\n• или просто Название")
                        continue

                    # Команда /help
                    if text == '/help':
                        send_message(chat_id, "📖 Как использовать:\n\n1. Отправь название трека\n2. Я найду его на YouTube\n3. Скачаю и отправлю тебе\n\nПримеры:\n• Rich Amiri - Never Fail\n• BRATAN\n• Скандалы и споры")
                        continue

                    # Парсим трек
                    track_info = parse_track(text)

                    if track_info:
                        process_track(chat_id, track_info)
                    else:
                        send_message(chat_id, "❓ Не понял запрос. Отправь название трека.")

            time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n🛑 Бот остановлен")
            break
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
