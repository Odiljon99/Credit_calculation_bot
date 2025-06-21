import telebot import os import time import threading from flask import Flask, request from telebot import types

TOKEN = os.environ.get("BOT_TOKEN") bot = telebot.TeleBot(TOKEN)

bot.set_my_commands([ types.BotCommand("start", "Boshlash / Начать"), ])

app = Flask(name) user_data = {}

translations = { "uz": { "start": "Assalomu alaykum! Tilni tanlang:", "choose_product": "Iltimos, kredit turini tanlang:", "product_options": ["🟢 Mikrokredit", "✍️ Mustaqil kiritish"], "client_type": "Iltimos, mijoz turini tanlang:", "months": "Iltimos, muddatni tanlang:", "salary": "Iltimos, oylik maoshingizni kiriting:", "other_loans": "Sizda boshqa kreditlar mavjudmi? (Ha/Yo'q)", "other_loans_amount": "Har oy boshqa kreditlarga qancha to'laysiz?", "result_limit": "Siz maksimal {limit} so'm kredit olishingiz mumkin.", "menu": "Quyidagilardan birini tanlang:", "new_calc": "🔁 Yangi hisob", "change_lang": "🌐 Tilni o'zgartirish", "client_types": ["Davlat xizmatchisi", "Xususiy sektor", "Pensioner"], "terms": { "Davlat xizmatchisi": ["24 oy - 25%", "36 oy - 26%", "48 oy - 27%"], "Xususiy sektor": ["24 oy - 30%", "36 oy - 31%", "48 oy - 32%"], "Pensioner": ["24 oy - 30%", "36 oy - 31%", "48 oy - 32%"] }, "months_error": "Faqat tugmalardan birini tanlang yoki to'g'ri son kiriting.", "amount_error": "Iltimos, to'g'ri summa kiriting.", }, "ru": { "start": "Здравствуйте! Пожалуйста, выберите язык:", "choose_product": "Пожалуйста, выберите тип кредита:", "product_options": ["\ud83d\udfe2 Микрокредит", "\u270d\ufe0f Самостоятельный ввод"], "client_type": "Пожалуйста, выберите тип клиента:", "months": "Пожалуйста, выберите срок:", "salary": "Пожалуйста, введите вашу зарплату:", "other_loans": "У вас есть другие кредиты? (Да/Нет)", "other_loans_amount": "Сколько вы платите за другие кредиты в месяц?", "result_limit": "Вы можете получить максимум {limit} сум кредита.", "menu": "Пожалуйста, выберите действие:", "new_calc": "\ud83d\udd01 Новый расчёт", "change_lang": "\ud83c\udf10 Изменить язык", "client_types": ["Госслужащий", "Частный сектор", "Пенсионер"], "terms": { "Госслужащий": ["24 мес - 25%", "36 мес - 26%", "48 мес - 27%"], "Частный сектор": ["24 мес - 30%", "36 мес - 31%", "48 мес - 32%"], "Пенсионер": ["24 мес - 30%", "36 мес - 31%", "48 мес - 32%"] }, "months_error": "Пожалуйста, выберите срок из кнопок или введите число.", "amount_error": "Пожалуйста, введите корректную сумму.", } }

loading_messages = [ "\ud83d\udee0\ufe0f Yuklanmoqda... / Загрузка...", "\u23f3 Maʼlumotlar tekshirilmoqda... / Проверка данных...", "\ud83e\udd16 Bot ishga tushirilmoqda... / Инициализация бота...", "\ud83d\ude80 Tayyorlanmoqda... / Подготовка..." ]

def format_number(n): return f"{n:,.0f}".replace(",", " ")

def send_language_selection(chat_id): markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) markup.add("\ud83c\uddfa\ud83c\uddff O'zbek", "\ud83c\uddf7\ud83c\uddfa Русский") bot.send_message(chat_id, translations["uz"]["start"], reply_markup=markup)

def send_main_menu(chat_id, lang): markup = types.ReplyKeyboardMarkup(resize_keyboard=True) markup.add(translations[lang]["new_calc"]) bot.send_message(chat_id, translations[lang]["menu"], reply_markup=markup)

def send_product_options(chat_id, lang): markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) for option in translations[lang]["product_options"]: markup.add(option) bot.send_message(chat_id, translations[lang]["choose_product"], reply_markup=markup)

def send_client_type_selection(chat_id, lang): markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) for ct in translations[lang]["client_types"]: markup.add(ct) bot.send_message(chat_id, translations[lang]["client_type"], reply_markup=markup)

def send_terms_selection(chat_id, lang, client_type): markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) for term in translations[lang]["terms"][client_type]: markup.add(term) bot.send_message(chat_id, translations[lang]["months"], reply_markup=markup)

def parse_months_and_rate(text): import re match = re.search(r"(\d+)[^\d]+(\d+)%", text) if match: return int(match.group(1)), float(match.group(2)) return None, None

def loading_sequence(chat_id): for msg in loading_messages: bot.send_message(chat_id, msg) time.sleep(2) send_language_selection(chat_id)

@bot.message_handler(commands=["start"]) def start(message): if message.message_thread_id is None: chat_id = message.chat.id user_data[chat_id] = {} threading.Thread(target=loading_sequence, args=(chat_id,)).start()

@bot.message_handler(func=lambda msg: True) def handle_message(message): if message.message_thread_id is not None: return

chat_id = message.chat.id
text = message.text.strip()

if chat_id not in user_data:
    user_data[chat_id] = {}
data = user_data[chat_id]

lang = data.get("lang", "uz")

if text in ["\ud83c\uddfa\ud83c\uddff O'zbek", "\ud83c\uddf7\ud83c\uddfa Русский", translations["uz"]["change_lang"], translations["ru"]["change_lang"]]:
    lang = "uz" if "O'zbek" in text else "ru"
    user_data[chat_id] = {"lang": lang}
    send_product_options(chat_id, lang)
    return

if text in [translations[lang]["new_calc"]]:
    user_data[chat_id] = {"lang": lang}
    send_product_options(chat_id, lang)
    return

if "product" not in data:
    if text in translations[lang]["product_options"]:
        data["product"] = text
        if "Mikro" in text or "\u041c\u0438\u043a\u0440\u043e" in text:
            send_client_type_selection(chat_id, lang)
    return

if "client_type" not in data:
    if text in translations[lang]["client_types"]:
        data["client_type"] = text
        send_terms_selection(chat_id, lang, text)
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
        bot.send_message(chat_id, translations[lang]["other_loans"])
    except:
        bot.send_message(chat_id, translations[lang]["amount_error"])
    return

if "has_other_loans" not in data:
    if text.lower() in ["yo'q", "нет", "no", "yoq"]:
        data["has_other_loans"] = False
        data["other_loans_amount"] = 0
        calculate_annuity_and_send(chat_id)
    elif text.lower() in ["ha", "да", "yes"]:
        data["has_other_loans"] = True
        bot.send_message(chat_id, translations[lang]["other_loans_amount"])
    return

if data.get("has_other_loans") and "other_loans_amount" not in data:
    try:
        data["other_loans_amount"] = float(text)
        calculate_annuity_and_send(chat_id)
    except:
        bot.send_message(chat_id, translations[lang]["amount_error"])

def calculate_annuity_and_send(chat_id): data = user_data[chat_id] lang = data["lang"]

salary = data["salary"]
months = data["months"]
rate = data["rate"] / 100
other = data.get("other_loans_amount", 0)

limit_monthly = (salary * 0.5) - other
monthly_rate = rate / 12
coefficient = (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
limit_credit = limit_monthly / coefficient

bot.send_message(chat_id, translations[lang]["result_limit"].format(limit=format_number(limit_credit)))

total = 0
result = ""
monthly = limit_monthly

for i in range(1, months + 1):
    result += f"{i}-oy: {format_number(monthly)} so'm\n" if lang == "uz" else f"{i}-мес: {format_number(monthly)} сум\n"
    total += monthly

bot.send_message(chat_id, result)
send_main_menu(chat_id, lang)
user_data.pop(chat_id)

@app.route(f"/{TOKEN}", methods=["POST"]) def webhook(): update = telebot.types.Update.de_json(request.stream.read().decode("utf-8")) bot.process_new_updates([update]) return "!", 200

@app.route("/", methods=["GET"]) def index(): return "Bot ishlayapti", 200

if name == "main": app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

