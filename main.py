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
        "amount": "Kredit summasini kiriting:",
        "months": "Iltimos, muddatni tanlang:",
        "client_type": "Iltimos, mijoz turini tanlang:",
        "amount_error": "Iltimos, to'g'ri summa kiriting.",
        "months_error": "Faqat quyidagi tugmalardan birini tanlang.",
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
        "amount": "Введите сумму кредита:",
        "months": "Пожалуйста, выберите срок:",
        "client_type": "Пожалуйста, выберите тип клиента:",
        "amount_error": "Пожалуйста, введите корректную сумму.",
        "months_error": "Выберите только одну из кнопок ниже.",
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
    markup.add(translations[lang]["new_calc"], translations[lang]["change_lang"])
    bot.send_message(chat_id, translations[lang]["menu"], reply_markup=markup)

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

@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    send_language_selection(chat_id)

@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text

    if chat_id not in user_data:
        user_data[chat_id] = {}

    data = user_data[chat_id]

    if text in ["🇺🇿 O'zbek", "🇷🇺 Русский", translations["uz"]["change_lang"], translations["ru"]["change_lang"]]:
        data.clear()
        data["lang"] = "uz" if "O'zbek" in text else "ru"
        bot.send_message(chat_id, translations[data["lang"]]["amount"])
        return

    if text in [translations["uz"]["new_calc"], translations["ru"]["new_calc"]]:
        lang = data.get("lang", "uz")
        user_data[chat_id] = {"lang": lang}
        bot.send_message(chat_id, translations[lang]["amount"])
        return

    if "lang" not in data:
        send_language_selection(chat_id)
        return

    lang = data["lang"]

    if "amount" not in data:
        try:
            data["amount"] = float(text)
            send_client_type_selection(chat_id, lang)
        except:
            bot.send_message(chat_id, translations[lang]["amount_error"])
    elif "client_type" not in data:
        if text in translations[lang]["client_types"]:
            data["client_type"] = text
            send_terms_selection(chat_id, lang, text)
        else:
            send_client_type_selection(chat_id, lang)
    elif "months" not in data:
        try:
            term_map = {
                "24": 24,
                "36": 36,
                "48": 48
            }
            num = ''.join(filter(str.isdigit, text))
            if num not in term_map:
                raise ValueError
            data["months"] = term_map[num]
            data["rate"] = get_rate(data["client_type"], data["months"], lang)
            calculate_and_send_result(chat_id)
            send_main_menu(chat_id, lang)
            user_data.pop(chat_id)
        except:
            bot.send_message(chat_id, translations[lang]["months_error"])

def get_rate(client_type, months, lang):
    if lang == "uz":
        if client_type == "Davlat xizmatchisi":
            return {24: 25, 36: 26, 48: 27}[months]
        else:
            return {24: 30, 36: 31, 48: 32}[months]
    else:
        if client_type == "Госслужащий":
            return {24: 25, 36: 26, 48: 27}[months]
        else:
            return {24: 30, 36: 31, 48: 32}[months]

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
