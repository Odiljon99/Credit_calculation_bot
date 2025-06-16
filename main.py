import telebot import os from flask import Flask, request from telebot import types

TOKEN = os.environ.get("BOT_TOKEN") bot = telebot.TeleBot(TOKEN)

✅ Добавляем команду /start в меню Telegram

bot.set_my_commands([ types.BotCommand("start", "Boshlash / Начать"), ])

app = Flask(name)

user_data = {}

translations = { "uz": { "start": "Assalomu alaykum! Tilni tanlang:", "amount": "Kredit summasini kiriting:", "months": "Necha oyga olmoqchisiz? (24, 36 yoki 48)", "client_type": "Iltimos, mijoz turini tanlang:", "amount_error": "Iltimos, to'g'ri summa kiriting.", "months_error": "Iltimos, 24, 36 yoki 48 oy kiriting.", "result": "Umumiy to'lov: {total:.2f} so'm", "menu": "Quyidagilardan birini tanlang:", "new_calc": "🔁 Yangi hisob", "change_lang": "🌐 Tilni o'zgartirish", "gos": "Davlat xizmatchisi", "private": "Xususiy sektor", "pensioner": "Pensioner" }, "ru": { "start": "Здравствуйте! Пожалуйста, выберите язык:", "amount": "Введите сумму кредита:", "months": "На сколько месяцев вы хотите взять? (24, 36 или 48)", "client_type": "Пожалуйста, выберите тип клиента:", "amount_error": "Пожалуйста, введите корректную сумму.", "months_error": "Пожалуйста, введите 24, 36 или 48 месяцев.", "result": "Общая сумма выплат: {total:.2f} сум", "menu": "Пожалуйста, выберите действие:", "new_calc": "🔁 Новый расчёт", "change_lang": "🌐 Изменить язык", "gos": "Госслужащий", "private": "Частный сектор", "pensioner": "Пенсионер" } }

rates = { "gos": {24: 25, 36: 26, 48: 27}, "private": {24: 30, 36: 31, 48: 32}, "pensioner": {24: 30, 36: 31, 48: 32} }

def send_language_selection(chat_id): markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) markup.add("🇺🇿 O'zbek", "🇷🇺 Русский") bot.send_message(chat_id, translations["uz"]["start"], reply_markup=markup)

def send_main_menu(chat_id, lang): markup = types.ReplyKeyboardMarkup(resize_keyboard=True) markup.add(translations[lang]["new_calc"], translations[lang]["change_lang"]) bot.send_message(chat_id, translations[lang]["menu"], reply_markup=markup)

def send_client_type_selection(chat_id, lang): markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) markup.add(translations[lang]["gos"], translations[lang]["private"], translations[lang]["pensioner"]) bot.send_message(chat_id, translations[lang]["client_type"], reply_markup=markup)

@bot.message_handler(commands=["start"]) def start(message): chat_id = message.chat.id user_data[chat_id] = {} send_language_selection(chat_id)

@bot.message_handler(func=lambda msg: True) def handle_message(message): chat_id = message.chat.id text = message.text

if chat_id not in user_data:
    user_data[chat_id] = {}

data = user_data[chat_id]

if text in ["🇺🇿 O'zbek", "🇷🇺 Русский", translations.get("uz", {}).get("change_lang"), translations.get("ru", {}).get("change_lang")]:
    data.clear()
    if "O'zbek" in text:
        data["lang"] = "uz"
    elif "Русский" in text:
        data["lang"] = "ru"
    bot.send_message(chat_id, translations[data["lang"]]["amount"])
    return

if text in [translations.get("uz", {}).get("new_calc"), translations.get("ru", {}).get("new_calc")]:
    lang = data.get("lang", "uz")
    user_data[chat_id] = {"lang": lang}
    bot.send_message(chat_id, translations[lang]["amount"])
    return

if "lang" not in data:
    bot.send_message(chat_id, "Iltimos, tilni tanlang:\nПожалуйста, выберите язык.")
    return

lang = data["lang"]

if "amount" not in data:
    try:
        data["amount"] = float(text)
        bot.send_message(chat_id, translations[lang]["months"])
    except:
        bot.send_message(chat_id, translations[lang]["amount_error"])
elif "months" not in data:
    try:
        months = int(text)
        if months not in [24, 36, 48]:
            raise ValueError()
        data["months"] = months
        send_client_type_selection(chat_id, lang)
    except:
        bot.send_message(chat_id, translations[lang]["months_error"])
elif "client_type" not in data:
    for key in ["gos", "private", "pensioner"]:
        if text == translations[lang][key]:
            data["client_type"] = key
            data["rate"] = rates[key][data["months"]]
            calculate_and_send_result(chat_id)
            send_main_menu(chat_id, lang)
            user_data.pop(chat_id)
            return
    send_client_type_selection(chat_id, lang)

def calculate_and_send_result(chat_id): data = user_data[chat_id] lang = data["lang"] amount = data["amount"] months = data["months"] rate = data["rate"] / 100

main_debt = amount / months
result = ""
total = 0

for i in range(months):
    remaining = amount - main_debt * i
    interest = remaining * rate / 12
    payment = main_debt + interest
    total += payment
    result += f"{i+1}-oy: {payment:.2f} so'm\n"

result += "\n" + translations[lang]["result"].format(total=total)
bot.send_message(chat_id, result)

@app.route(f"/{TOKEN}", methods=["POST"]) def webhook(): bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))]) return "!", 200

@app.route("/", methods=["GET"]) def index(): return "Bot ishlayapti", 200

if name == "main": app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

