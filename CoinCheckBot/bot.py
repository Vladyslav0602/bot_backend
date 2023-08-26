import telebot
from currency_converter import CurrencyConverter
from telebot import types


bot = telebot.TeleBot('6042844303:AAFRi4g-WWzivX2OqG0Pw4Fwa8LRX1b-lEA')
currency = CurrencyConverter()

amount = 0


@bot.message_handler(commands=['/start'])
def start(message):
    bot.send_message(message.chat.id, 'Привіт чим я можу допомогти?')


def summa(message):
    global amount
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, 'Задано невірний формат. Будь ласка впишіть сумму')
        bot.register_next_step_handler(message, summa)

    if amount > 0:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton('USD/UAH', callback_data='usd/uah')
        btn2 = types.InlineKeyboardButton('EUR/UAH', callback_data='eur/uah')
        btn3 = types.InlineKeyboardButton('UAH/USD', callback_data='uah/usd')
        btn4 = types.InlineKeyboardButton('UAH/EUR', callback_data='uah/eur')
        btn5 = types.InlineKeyboardButton('Інше', callback_data='else')
        markup.add(btn1, btn2, btn3, btn4, btn5)
        bot.send_message(message.chat.id, 'Оберіть пару валют', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Число має бути більшим ніж нуль. Будь ласка впишіть сумму')
        bot.register_next_step_handler(message, summa)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    values = call.data.upper().split('/')
    res = currency.convert(amount, values[0], values[1])
    bot.send_message(call.message.chat.id, f'Результат: {res}. Вкажіть сумму для повторної конвертації')
    bot.register_next_step_handler(call.message, summa)

bot.polling(none_stop=True)