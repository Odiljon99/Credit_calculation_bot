import telebot
import os
from flask import Flask, request

TOKEN = "7730388073:AAHu8bjQRzrvOb6Cpn1EpXn-kWVhTSEN0QI"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_data = {}

@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    bot.send_message(chat_id, "Assalomu alaykum! Kredit summasini kiriting:")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text

    if chat_id not in user_data:
        user_data[chat_id] = {}

    data = user_data[chat_id]

    if "amount" not in data:
        try:
            data["amount"] = float(text)
            bot.send_message(chat_id, "Necha oyga olmoqchisiz?")
        except:
            bot.send_message(chat_id, "Iltimos, to'g'ri summa kiriting.")
    elif "months" not in data:
        try:
            data["months"] = int(text)
            bot.send_message(chat_id, "Foiz stavkasini kiriting (%):")
        except:
            bot.send_message(chat_id, "Iltimos, to'g'ri oy sonini kiriting.")
    elif "rate" not in data:
        try:
            data["rate"] = float(text)
            calculate_and_send_result(chat_id)
            user_data.pop(chat_id)
        except:
            bot.send_message(chat_id, "Iltimos, to'g'ri foiz stavkasini kiriting.")

def calculate_and_send_result(chat_id):
    data = user_data[chat_id]
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
        result += f"{i+1}-oy: {payment:.2f} so'm\n"

    result += f"Umumiy to'lov: {total:.2f} so'm"
    bot.send_message(chat_id, result)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot ishlayapti", 200

if __name__ == "__main__":
    app.run(debug=True)