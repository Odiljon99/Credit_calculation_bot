import telebot
import os
import time
import threading
from flask import Flask, request
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

bot.set_my_commands([
    types.BotCommand("start", "Boshlash / Начать"),
])

app = Flask(__name__)
user_data = {}

translations = {
    "uz": {
        "start": "Assalomu alaykum! Tilni tanlang:",
        "choose_product": "Iltimos, kredit turini tanlang:",
        "product_options": ["🟢 Mikrokredit", "✍️ Mustaqil kiritish"],
        "client_type": "Iltimos, mijoz turini tanlang:",
        "months": "Iltimos, muddatni tanlang:",
        "salary": "Iltimos, oylik maoshingizni kiriting:",
        "other_loans": "Sizda boshqa kreditlar mavjudmi?",
        "other_loans_amount": "Har oy boshqa kreditlarga qancha to'laysiz?",
        "result_limit": "Siz maksimal {limit} so'm kredit olishingiz mumkin.",
        "menu": "Quyidagilardan birini tanlang:",
        "new_calc": "🔁 Yangi hisob",
        "change_lang": "🌐 Tilni o'zgartirish",
        "client_types": ["Davlat xizmatchisi", "Xususiy sektor", "Pensioner"],
        "terms": {
            "Davlat xizmatchisi": ["24 oy - 25%", "36 oy - 26%", "48 oy - 27%"],
            "Xususiy sektor": ["24 oy - 30%", "36 oy - 31%", "48 oy - 32%"],
            "Pensioner": ["24 oy - 30%", "36 oy - 31%", "48 oy - 32%"]
        },
        "months_error": "Faqat tugmalardan birini tanlang yoki to'g'ri son kiriting.",
        "amount_error": "Iltimos, to'g'ri summa kiriting.",
    },
    "ru": {
        "start": "Здравствуйте! Пожалуйста, выберите язык:",
        "choose_product": "Пожалуйста, выберите тип кредита:",
        "product_options": ["🟢 Микрокредит", "✍️ Самостоятельный ввод"],
        "client_type": "Пожалуйста, выберите тип клиента:",
        "months": "Пожалуйста, выберите срок:",
        "salary": "Пожалуйста, введите вашу зарплату:",
        "other_loans": "У вас есть другие кредиты?",
        "other_loans_amount": "Сколько вы платите за другие кредиты в месяц?",
        "result_limit": "Вы можете получить максимум {limit} сум кредита.",
        "menu": "Пожалуйста, выберите действие:",
        "new_calc": "🔁 Новый расчёт",
        "change_lang": "🌐 Изменить язык",
        "client_types": ["Госслужащий", "Частный сектор", "Пенсионер"],
        "terms": {
            "Госслужащий": ["24 мес - 25%", "36 мес - 26%", "48 мес - 27%"],
            "Частный сектор": ["24 мес - 30%", "36 мес - 31%", "48 мес - 32%"],
            "Пенсионер": ["24 мес - 30%", "36 мес - 31%", "48 мес - 32%"]
        },
        "months_error": "Пожалуйста, выберите срок из кнопок или введите число.",
        "amount_error": "Пожалуйста, введите корректную сумму.",
    }
}

def format_number(n):
    return f"{n:,.0f}".replace(",", " ")

def send_keyboard(chat_id, text, buttons):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for row in buttons:
        markup.add(*row)
    bot.send_message(chat_id, text, reply_markup=markup)

def parse_months_and_rate(text):
    import re
    match = re.search(r"(\d+)[^\d]+(\d+)%", text)
    if match:
        return int(match.group(1)), float(match.group(2))
    return None, None

def loading_sequence(chat_id):
    for msg in [
        "🛠️ Yuklanmoqda... / Загрузка...",
        "⏳ Maʼlumotlar tekshirilmoqda... / Проверка данных...",
        "🤖 Bot ishga tushirilmoqda... / Инициализация бота...",
        "🚀 Tayyorlanmoqda... / Подготовка..."
    ]:
        bot.send_message(chat_id, msg)
        time.sleep(1.5)
    send_keyboard(chat_id, translations["uz"]["start"], [["🇺🇿 O'zbek", "🇷🇺 Русский"]])

@bot.message_handler(commands=["start"])
def start(message):
    if message.message_thread_id is None:
        chat_id = message.chat.id
        user_data[chat_id] = {}
        threading.Thread(target=loading_sequence, args=(chat_id,)).start()

@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    if message.message_thread_id is not None:
        return
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_data:
        user_data[chat_id] = {}
    data = user_data[chat_id]
    lang = data.get("lang", "uz")

    if text in ["🇺🇿 O'zbek", "🇷🇺 Русский", translations["uz"]["change_lang"], translations["ru"]["change_lang"]]:
        lang = "uz" if "O'zbek" in text else "ru"
        user_data[chat_id] = {"lang": lang}
        send_keyboard(chat_id, translations[lang]["choose_product"], [[p] for p in translations[lang]["product_options"]])
        return

    if text in [translations["uz"]["new_calc"], translations["ru"]["new_calc"]]:
        lang = user_data[chat_id].get("lang", "uz")
        user_data[chat_id].clear()  # очищаем всё, кроме языка
        user_data[chat_id]["lang"] = lang
        send_keyboard(chat_id, translations[lang]["choose_product"], [[p] for p in translations[lang]["product_options"]])
        return

    if "product" not in data:
        if text in translations[lang]["product_options"]:
            data["product"] = text
            send_keyboard(chat_id, translations[lang]["client_type"], [[t] for t in translations[lang]["client_types"]])
        return

    if "client_type" not in data:
        if text in translations[lang]["client_types"]:
            data["client_type"] = text
            send_keyboard(chat_id, translations[lang]["months"], [[t] for t in translations[lang]["terms"][text]])
        return

    if "months" not in data:
        months, rate = parse_months_and_rate(text)
        if not months:
            bot.send_message(chat_id, translations[lang]["months_error"])
        else:
            data["months"] = months
            data["rate"] = rate
            bot.send_message(chat_id, translations[lang]["salary"])
        return

    if "salary" not in data:
        try:
            data["salary"] = float(text)
            send_keyboard(chat_id, translations[lang]["other_loans"],
                          [["✅ Ha", "❌ Yo'q"]] if lang == "uz" else [["✅ Да", "❌ Нет"]])
        except:
            bot.send_message(chat_id, translations[lang]["amount_error"])
        return

    if "has_other_loans" not in data:
        if text.lower() in ["yo'q", "нет", "no", "yoq", "❌ yo'q", "❌ нет"]:
            data["has_other_loans"] = False
            data["other_loans_amount"] = 0
            calculate_diff_and_send(chat_id)
        elif text.lower() in ["ha", "да", "yes", "✅ ha", "✅ да"]:
            data["has_other_loans"] = True
            bot.send_message(chat_id, translations[lang]["other_loans_amount"])
        return

    if data.get("has_other_loans") and "other_loans_amount" not in data:
        try:
            data["other_loans_amount"] = float(text)
            calculate_diff_and_send(chat_id)
        except:
            bot.send_message(chat_id, translations[lang]["amount_error"])

def calculate_diff_and_send(chat_id):
    data = user_data[chat_id]
    lang = data["lang"]
    salary = data["salary"]
    months = data["months"]
    rate = data["rate"] / 100
    other = data.get("other_loans_amount", 0)

    limit_monthly = (salary * 0.5) - other
    monthly_rate = rate / 12

    main_limit = limit_monthly * months / (1 + monthly_rate * (months + 1) / 2)
    total = 0
    result = ""

    for i in range(1, months + 1):
        principal = main_limit / months
        interest = (main_limit - principal * (i - 1)) * monthly_rate
        payment = principal + interest
        total += payment
        result += f"{i}-oy: {format_number(payment)} so'm\n" if lang == "uz" else f"{i}-мес: {format_number(payment)} сум\n"

    bot.send_message(chat_id, translations[lang]["result_limit"].format(limit=format_number(main_limit)))
    bot.send_message(chat_id, result)
    send_keyboard(chat_id, translations[lang]["menu"], [[translations[lang]["new_calc"]]])
    user_data.pop(chat_id)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "!", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot ishlayapti", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
