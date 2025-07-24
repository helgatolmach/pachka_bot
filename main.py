import os
import json
import tempfile
import datetime
from datetime import datetime, timezone, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests


API_TOKEN = os.getenv("API_TOKEN")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")
CHAT_ID = os.getenv ("CHAT_ID")

# --- Настройки ---

# Московское время +3 UTC
moscow_offset = timedelta(hours=3)
moscow_tz = timezone(moscow_offset, name="MSK")

# Время отправки сообщений — 8:00 по Москве
SEND_HOUR = 8

# Получаем JSON с ключами из переменной окружения
creds_json_str = os.getenv("GOOGLE_CREDENTIALS_JSON")

# Создаем временный файл с содержимым
with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp:
    temp.write(creds_json_str)
    temp.flush()
    creds_file_path = temp.name

# Авторизация с помощью временного файла
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file_path, SCOPE)

# После этого можно удалить временный файл (если хочешь)

os.remove(creds_file_path)

# Google Таблица и доступ к ней
SPREADSHEET_NAME = "Поздравлялка"  # Имя таблицы

# API Пачки
API_URL = "https://crm.pachca.com/api/send_message"

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}

# Праздники с датами в формате "дд.мм"
HOLIDAYS = {
    "01.01": "С Новым годом!",
    "08.03": "С 8 марта!",
    "23.02": "С 23 февраля!",
    "01.05": "С праздником Весны и Труда!",
    "09.05": "С Днём Победы!",
    "12.06": "С Днём России!",
    "24.07": "С праздником! 🎉 (Тестовая дата)"
}


def send_message(text: str):
    """Функция отправки сообщения в Пачку"""
    payload = {
        "entity_id": CHAT_ID,
        "message": text
    }
    try:
        response = requests.post(API_URL, json=payload, headers=HEADERS)
        response.raise_for_status()
        print(f"Отправлено сообщение: {text}")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")


def main():
    # Проверяем, что сейчас нужный час (8:00 МСК)
    now = datetime.now(moscow_tz)
    if now.hour != SEND_HOUR:
        print(f"Сейчас не время отправки сообщений. Время: {now.strftime('%H:%M')}. Выход.")
        return

    # Авторизация и подключение к Google Таблице
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds, SCOPE)
    client = gspread.authorize(creds)

    sheet = client.open(SPREADSHEET_NAME).sheet1
    rows = sheet.get_all_records()

    today_str = now.strftime("%d.%m")

    # Отправляем поздравления с днем рождения
    for row in rows:
        # В таблице предполагаем, что дата рождения в формате строка "дд.мм" или число
        birthday_raw = row.get('Birthday')
        if birthday_raw is None:
            continue

        # Приводим дату к строке в формате "дд.мм"
        if isinstance(birthday_raw, float) or isinstance(birthday_raw, int):
            # Если дата в виде числа с точкой, например 24.07
            birthday_str = f"{birthday_raw:.2f}".replace('.', '.')
        else:
            birthday_str = str(birthday_raw).strip()

        if birthday_str == today_str:
            name = row.get('Name', 'коллега')
            # Формируем сообщение с упоминанием
            message = f"🎉 Сегодня день рождения у @{name}! Поздравим!"
            send_message(message)

    # Отправляем поздравления с праздниками
    if today_str in HOLIDAYS:
        holiday_message = HOLIDAYS[today_str]
        send_message(f"🎉 {holiday_message}")


if __name__ == "__main__":
    main()
