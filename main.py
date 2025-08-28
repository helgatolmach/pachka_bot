import os
from tempfile import NamedTemporaryFile
import datetime
import gspread
from datetime import datetime, timezone, timedelta
import requests
from oauth2client.service_account import ServiceAccountCredentials



API_TOKEN = os.getenv("API_TOKEN")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")
CHAT_ID = os.getenv ("CHAT_ID")

# --- Настройки ---

# Московское время +3 UTC
moscow_offset = timedelta(hours=3)
moscow_tz = timezone(moscow_offset, name="MSK")


creds_dict = {
    "type": os.getenv("TYPE"),
    "project_id": os.getenv("PROJECT_ID"),
    "private_key_id": os.getenv("PRIVATE_KEY_ID"),
    "private_key": os.getenv("PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("CLIENT_EMAIL"),
    "client_id": os.getenv("CLIENT_ID"),
    "auth_uri": os.getenv("AUTH_URI"),
    "token_uri": os.getenv("TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
    "universe_domain": os.getenv("UNIVERSE_DOMAIN"),
}


# API Пачки
API_URL = "https://api.pachca.com/api/shared/v1/messages"

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}


def send_message(text: str):
    """Функция отправки сообщения в Пачку"""
    payload = {
        "message": {
            "entity_id": CHAT_ID,
            "content": text
        }
    }
    try:
        response = requests.post(API_URL, json=payload, headers=HEADERS)
        response.raise_for_status()
        print(f"Отправлено сообщение: {text}")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")


def main():

    from tempfile import NamedTemporaryFile
    with NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as tmp:
        import json
        json.dump(creds_dict, tmp)
        tmp.flush()
        creds_file_path = tmp.name


    SCOPE = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file_path, SCOPE)

    client = gspread.authorize(creds)

    sheet = client.open_by_key(SPREADSHEET_NAME)
    worksheet = sheet.sheet1
    rows = worksheet.get_all_records()

    now = datetime.now(moscow_tz)
    today_str = now.strftime("%d.%m")

    # Отправляем поздравления с днем рождения
    for row in rows:
        # В таблице предполагаем, что дата рождения в формате строка "дд.мм" или число
        date_str = str(row.get('Date'))

        if date_str == today_str:
            type = row.get('Type')
            if type == "Birthday":
                name = row.get('Name', 'коллега')
                # Формируем сообщение с упоминанием
                message = f"🎉 Сегодня день рождения у @{name}! Поздравим!"
                send_message(message)
            elif type == "Holiday":
                name = row.get('Name')
                message = f"Сегодня {name}! С праздником, коллеги!"
                send_message(message)


if __name__ == "__main__":
    main()
