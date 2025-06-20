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
        "has_loans": "Sizda boshqa kreditlar mavjudmi? (Ha/Yo'q)",
        "loan_payment": "Iltimos, mavjud kreditlaringiz bo'yicha oylik to'lov summasini kiriting:",
        "limit_result": "Siz maksimal {amount} so'm kredit olishingiz mumkin.",
        "amount_error": "Iltimos, to'g'ri summa kiriting.",
        "months_error": "Faqat tugmalardan birini tanlang yoki to'g'ri son kiriting.",
        "rate_error": "Iltimos, to'g'ri foiz stavkasini kiriting.",
        "result": "Umumiy to'lov: {total} so'm",
        "menu": "Quyidagilardan birini tanlang:",
        "new_calc": "🔁 Yangi hisob",
        "change_lang": "🌐 Tilni o'zgartirish",
        "client_types": ["Davlat xizmatchisi", "Xususiy sektor", "Pensioner"],
        "terms": {
            "Davlat xizmatchisi": ["24 oy - 25%", "36 oy - 26%", "48 oy - 27%"],
            "Xususiy sektor": ["24 oy - 30%", "36 oy - 31%", "48 oy - 32%"],
            "Pensioner": ["24 oy - 30%", "36 oy - 31%", "48 oy - 32%"]
        }
    },
    "ru": {
        "start": "Здравствуйте! Пожалуйста, выберите язык:",
        "choose_product": "Пожалуйста, выберите тип кредита:",
        "product_options": ["🟢 Микрокредит", "✍️ Самостоятельный ввод"],
        "client_type": "Пожалуйста, выберите тип клиента:",
        "months": "Пожалуйста, выберите срок:",
        "salary": "Введите вашу ежемесячную зарплату:",
        "has_loans": "У вас есть другие кредиты? (Да/Нет)",
        "loan_payment": "Введите сумму ежемесячных выплат по другим кредитам:",
        "limit_result": "Вы можете получить максимум {amount} сум кредита.",
        "amount_error": "Пожалуйста, введите корректную сумму.",
        "months_error": "Пожалуйста, выберите срок из кнопок или введите число.",
        "rate_error": "Пожалуйста, введите корректную процентную ставку.",
        "result": "Общая сумма выплат: {total} сум",
        "menu": "Пожалуйста, выберите действие:",
        "new_calc": "🔁 Новый расчёт",
        "change_lang": "🌐 Изменить язык",
        "client_types": ["Госслужащий", "Частный сектор", "Пенсионер"],
        "terms": {
            "Госслужащий": ["24 мес - 25%", "36 мес - 26%", "48 мес - 27%"],
            "Частный сектор": ["24 мес - 30%", "36 мес - 31%", "48 мес - 32%"],
            "Пенсионер": ["24 мес - 30%", "36 мес - 31%", "48 мес - 32%"]
        }
    }
}

loading_messages = [
    "🛠️ Yuklanmoqda... / Загрузка...",
    "⏳ Maʼlumotlar tekshirilmoqda... / Проверка данных...",
    "🤖 Bot ishga tushirilmoqda... / Инициализация бота...",
    "🚀 Tayyorlanmoqda... / Подготовка..."
]

def send_language_selection(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("🇺🇿 O'zbek", "🇷🇺 Русский")
    bot.send_message(chat_id, translations["uz"]["start"], reply_markup=markup)

def send_main_menu(chat_id, lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(translations[lang]["new_calc"])
    bot.send_message(chat_id, translations[lang]["menu"], reply_markup=markup)

def send_product_options(chat_id, lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for option in translations[lang]["product_options"]:
        markup.add(option)
    bot.send_message(chat_id, translations[lang]["choose_product"], reply_markup=markup)

def send_client_type_selection(chat_id, lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for ct in translations[lang]["client_types"]:
        markup.add(ct)
    bot.send_message(chat_id, translations[lang]["client_type"], reply_markup=markup)

def send_terms_selection(chat_id, lang, client_type):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for term in translations[lang]["terms"][client_type]:
        markup.add(term)
    bot.send_message(chat_id, translations[lang]["months"], reply_markup=markup)

def parse_months_and_rate(text):
    import re
    match = re.search(r"(\d+)[^\d]+(\d+)%", text)
    if match:
        return int(match.group(1)), float(match.group(2))
    return None, None

def format_number(n):
    return f"{n:,.0f}".replace(",", " ")

def loading_sequence(chat_id):
    for msg in loading_messages:
        bot.send_message(chat_id, msg)
        time.sleep(1.5)
    send_language_selection(chat_id)

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
        send_product_options(chat_id, lang)
        return

    if text in [translations["uz"]["new_calc"], translations["ru"]["new_calc"]]:
        user_data[chat_id] = {"lang": lang}
        send_product_options(chat_id, lang)
        return

    if "lang" not in data:
        send_language_selection(chat_id)
        return

    if "product" not in data:
        if text in translations[lang]["product_options"]:
            data["product"] = text
            if "Mikro" in text or "Микро" in text:
                send_client_type_selection(chat_id, lang)
            else:
                bot.send_message(chat_id, translations[lang]["salary"])
        else:
            send_product_options(chat_id, lang)
        return

    if data["product"].startswith("🟢"):
        if "client_type" not in data:
            if text in translations[lang]["client_types"]:
                data["client_type"] = text
                send_terms_selection(chat_id, lang, text)
            else:
                send_client_type_selection(chat_id, lang)
        elif "months" not in data:
            months, rate = parse_months_and_rate(text)
            if months:
                data["months"], data["rate"] = months, rate
                bot.send_message(chat_id, translations[lang]["salary"])
            else:
                bot.send_message(chat_id, translations[lang]["months_error"])
        elif "salary" not in data:
            try:
                data["salary"] = float(text)
                bot.send_message(chat_id, translations[lang]["has_loans"])
            except:
                bot.send_message(chat_id, translations[lang]["amount_error"])
        elif "has_loans" not in data:
            if text.lower() in ["ha", "да"]:
                data["has_loans"] = True
                bot.send_message(chat_id, translations[lang]["loan_payment"])
            elif text.lower() in ["yo'q", "нет"]:
                data["has_loans"] = False
                data["loan_payment"] = 0
                suggest_max_credit(chat_id)
            else:
                bot.send_message(chat_id, translations[lang]["has_loans"])
        elif data.get("has_loans") and "loan_payment" not in data:
            try:
                data["loan_payment"] = float(text)
                suggest_max_credit(chat_id)
            except:
                bot.send_message(chat_id, translations[lang]["amount_error"])
    else:
        bot.send_message(chat_id, "Bu qism hali ishlab chiqilmoqda. / Эта часть пока в разработке.")

def suggest_max_credit(chat_id):
    data = user_data[chat_id]
    lang = data["lang"]
    salary = data["salary"]
    max_monthly = salary * 0.5 - data["loan_payment"]
    months = data["months"]
    rate = data["rate"] / 100 / 12

    max_credit = (max_monthly / (1 / months + rate / 2)) * months
    max_credit = max(0, round(max_credit, 2))

    bot.send_message(chat_id, translations[lang]["limit_result"].format(amount=format_number(max_credit)))
    calculate_and_send_result(chat_id, max_credit)

def calculate_and_send_result(chat_id, amount):
    data = user_data[chat_id]
    lang = data["lang"]
    months = data["months"]
    rate = data["rate"] / 100

    main_debt = amount / months
    result = ""
    total = 0

    for i in range(months):
        interest = (amount - main_debt * i) * rate / 12
        payment = main_debt + interest
        total += payment
        line = f"{i+1}-oy: {format_number(payment)} so'm" if lang == "uz" else f"{i+1}-мес: {format_number(payment)} сум"
        result += line + "\n"

    total_text = translations[lang]["result"].format(total=format_number(total))
    result += "\n" + total_text
    bot.send_message(chat_id, result)
    send_main_menu(chat_id, lang)
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
