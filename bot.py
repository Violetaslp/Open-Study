import telebot
from telebot import types
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
TOKEN = os.environ.get("TOKEN")

# --- Настройки ---
SPREADSHEET_NAME = "Заявки OpenStudy"

bot = telebot.TeleBot(TOKEN)

# --- Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open(SPREADSHEET_NAME).worksheet("Лист1")

# --- Память для данных пользователя ---
user_data = {}

# --- Команда /start ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Пробный урок")
    btn2 = types.KeyboardButton("Бесплатный семинар")
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Привет! 👋 Выберите вариант ниже:", reply_markup=markup)

# --- Обработка выбора ---
@bot.message_handler(func=lambda m: m.text in ["Пробный урок", "Бесплатный семинар"])
def handle_choice(message):
    user_data[message.chat.id] = {"type": message.text, "username": message.from_user.username}
    bot.send_message(message.chat.id, "Введите ваше имя и фамилию:")
    bot.register_next_step_handler(message, get_name)

# --- Получение имени ---
def get_name(message):
    user_data[message.chat.id]["name"] = message.text
    bot.send_message(message.chat.id, "Введите ваш номер телефона:")
    bot.register_next_step_handler(message, get_phone)

# --- Получение телефона и запись в Google Sheets ---
def get_phone(message):
    user_data[message.chat.id]["phone"] = message.text
    data = user_data[message.chat.id]

    # Текущее время
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Запись в Google Sheets
    # Столбцы: Дата и время | Chat ID | Имя | Телефон | Тип заявки | Username | Обработано
    sheet.append_row([
        timestamp,
        data["name"],
        data["phone"],
        data["type"],
        data["username"],

    ])

    bot.send_message(message.chat.id, f"✅ Ваша заявка на '{data['type']}' принята! Мы свяжемся с вами скоро.")
    del user_data[message.chat.id]

# --- Запуск бота ---
print("Бот запущен...")
bot.polling(none_stop=True)
