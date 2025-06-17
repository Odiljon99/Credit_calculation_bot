import telebot
import os
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
        "amount": "Kredit summasini kiriting:",
        "rate": "Foiz stavkasini kiriting (masalan, 28):",
        "amount_error": "Iltimos, to'g'ri summa kiriting.",
        "months_error": "Faqat tugmalardan birini tanlang yoki to'g'ri son kiriting.",
        "rate_error": "Iltimos, to'g'ri foiz stavkasini kiriting.",
        "result": "Umumiy to'lov: {total:.2f} so'm",
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
        "amount": "Введите сумму кредита:",
        "rate": "Введите процентную ставку (например, 28):",
        "amount_error": "Пожалуйста, введите корректную сумму.",
        "months_error": "Пожалуйста, выберите срок из кнопок или введите число.",
        "rate_error": "Пожалуйста, введите корректную процентную ставку.",
        "result": "Общая сумма выплат: {total:.2f} сум",
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

def send_language_selection(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("🇺🇿 O'zbek", "🇷🇺 Русский")
    bot.send_message(chat_id, translations["uz"]["start"], reply_markup=markup)

def send_main_menu(chat_id, lang):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(translations[lang]["new_calc"])  # ❗ Удалили кнопку "change_lang"
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
        months = int(match.group(1))
        rate = float(match.group(2))
        return months, rate
    return None, None

@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    send_language_selection(chat_id)

@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id not in user_data:
        user_data[chat_id] = {}

    data = user_data[chat_id]

    if text in ["🇺🇿 O'zbek", "🇷🇺 Русский", translations["uz"]["change_lang"], translations["ru"]["change_lang"]]:
        lang = "uz" if "O'zbek" in text else "ru"
        user_data[chat_id] = {"lang": lang}
        send_product_options(chat_id, lang)
        return

    if text in [translations["uz"]["new_calc"], translations["ru"]["new_calc"]]:
        lang = data.get("lang", "uz")
        user_data[chat_id] = {"lang": lang}
        send_product_options(chat_id, lang)
        return

    if "lang" not in data:
        send_language_selection(chat_id)
        return

    lang = data["lang"]

    if "product" not in data:
        if text in translations[lang]["product_options"]:
            data["product"] = text
            if "Mikro" in text or "Микро" in text:
                send_client_type_selection(chat_id, lang)
            else:
                bot.send_message(chat_id, translations[lang]["amount"])
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
            try:
                months, rate = parse_months_and_rate(text)
                if not months or not rate:
                    raise ValueError("Invalid format")
                data["months"] = months
                data["rate"] = rate
                bot.send_message(chat_id, translations[lang]["amount"])
            except:
                bot.send_message(chat_id, translations[lang]["months_error"])
        elif "amount" not in data:
            try:
                data["amount"] = float(text)
                calculate_and_send_result(chat_id)
                send_main_menu(chat_id, lang)
                user_data.pop(chat_id)
            except:
                bot.send_message(chat_id, translations[lang]["amount_error"])
    else:
        if "amount" not in data:
            try:
                data["amount"] = float(text)
                bot.send_message(chat_id, translations[lang]["months"])
            except:
                bot.send_message(chat_id, translations[lang]["amount_error"])
        elif "months" not in data:
            try:
                data["months"] = int(text)
                bot.send_message(chat_id, translations[lang]["rate"])
            except:
                bot.send_message(chat_id, translations[lang]["months_error"])
        elif "rate" not in data:
            try:
                data["rate"] = float(text)
                calculate_and_send_result(chat_id)
                send_main_menu(chat_id, lang)
                user_data.pop(chat_id)
            except:
                bot.send_message(chat_id, translations[lang]["rate_error"])

def calculate_and_send_result(chat_id):
    data = user_data[chat_id]
    lang = data["lang"]
    amount = data["amount"]
    months = data["months"]
    rate = data["rate"] / 100

    main_debt = amount / months
    result = ""
    total = 0

    for i in range(months):
        remaining = amount - main_debt * i
        interest = remaining * rate / 12
        payment = main_debt + interest
        total += payment
        result += f"{i+1}-oy: {payment:.2f} so'm\n" if lang == "uz" else f"{i+1}-мес: {payment:.2f} сум\n"

    result += "\n" + translations[lang]["result"].format(total=total)
    bot.send_message(chat_id, result)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot ishlayapti", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
