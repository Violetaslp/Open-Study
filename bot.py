import os
import json
import telebot
from telebot import types
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- Telegram Token ---
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("TOKEN не найден! Установите переменную окружения на Render.")

bot = telebot.TeleBot(TOKEN)

creds_json = os.environ.get("GOOGLE_CREDENTIALS")
if not creds_json:
    raise ValueError("GOOGLE_CREDENTIALS не найден! Установите Secret в Render.")

creds_dict = json.loads(creds_json)

credentials_dict = json.loads(credentials_json)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(credentials)

SPREADSHEET_NAME = "Заявки OpenStudy"
sheet = client.open(SPREADSHEET_NAME).worksheet("Лист1")

user_data = {}

# --- Команды бота ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Пробный урок")
    btn2 = types.KeyboardButton("Бесплатный семинар")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Привет! 👋 Выберите вариант ниже:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["Пробный урок", "Бесплатный семинар"])
def handle_choice(message):
    user_data[message.chat.id] = {"type": message.text, "username": message.from_user.username}
    bot.send_message(message.chat.id, "Введите ваше имя и фамилию:")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    user_data[message.chat.id]["name"] = message.text
    bot.send_message(message.chat.id, "Введите ваш номер телефона:")
    bot.register_next_step_handler(message, get_phone)

def get_phone(message):
    data = user_data[message.chat.id]
    data["phone"] = message.text
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Запись в Google Sheets
    sheet.append_row([timestamp, data["name"], data["phone"], data["type"], data["username"], False])

    bot.send_message(message.chat.id, f"✅ Ваша заявка на '{data['type']}' принята!")
    del user_data[message.chat.id]

if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(none_stop=True)
