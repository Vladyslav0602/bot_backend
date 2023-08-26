import requests
import telebot
from currency_converter import CurrencyConverter
from telebot import types


bot = telebot.TeleBot('6042844303:AAFRi4g-WWzivX2OqG0Pw4Fwa8LRX1b-lEA')
currency = CurrencyConverter()

amount = 0
waiting_for_commands_command = False
waiting_for_convert_command = False


@bot.message_handler(commands=['start'])
def start(message):
    global waiting_for_commands_command
    bot.send_message(message.chat.id, 'Привіт чим я можу допомогти? Щоб подивитися список можливих команд /commands')
    waiting_for_commands_command = True
    bot.register_next_step_handler(message, show_commands)


@bot.message_handler(commands=['convert'])
def convert(message):
    global waiting_for_convert_command
    waiting_for_convert_command = True
    bot.send_message(message.chat.id, 'Введіть сумму для конвертації')
    bot.register_next_step_handler(message, summa)


def summa(message):
    global amount
    global waiting_for_convert_command
    try:
        amount = int(message.text.strip())
        if amount <= 0:
            bot.send_message(message.chat.id, 'Число має бути більшим ніж нуль. Будь ласка впишіть сумму')
            bot.register_next_step_handler(message, summa)
            return
    except ValueError:
        bot.send_message(message.chat.id, 'Задано невірний формат. Будь ласка впишіть сумму')
        bot.register_next_step_handler(message, summa)

    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('USD/GBP', callback_data='usd/gbp')
    btn2 = types.InlineKeyboardButton('EUR/GBP', callback_data='eur/gbp')
    btn3 = types.InlineKeyboardButton('GBP/USD', callback_data='gbp/usd')
    btn4 = types.InlineKeyboardButton('GBP/EUR', callback_data='gbp/eur')
    btn5 = types.InlineKeyboardButton('Інше', callback_data='else')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    bot.send_message(message.chat.id, 'Оберіть пару валют', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data != 'else':
        values = call.data.upper().split('/')

        if len(values) != 2:
            bot.send_message(call.message.chat.id, 'Неправильний формат валютної пари. Виберіть іншу пару')
            bot.register_next_step_handler(call.message, summa)
            return

        try:
            res = currency.convert(amount, values[0], values[1])
            res_rounded = round(res, 2)
            bot.send_message(call.message.chat.id, f'Результат: {res_rounded}. Вкажіть сумму для повторної конвертації')
            bot.register_next_step_handler(call.message, summa)
        except ValueError:
            bot.send_message(call.message.chat.id, 'Непідтримувана валюта. Виберіть іншу валютну пару')
            bot.register_next_step_handler(call.message, summa)
    else:
        bot.send_message(call.message.chat.id, 'Введіть пару абревіатур валют через слеш')
        bot.register_next_step_handler(call.message, my_currency)


def my_currency(message):
    values = message.text.upper().split('/')
    if len(values) != 2:
        bot.send_message(message.chat.id, 'Неправильний формат валютної пари. Виберіть іншу пару')
        bot.register_next_step_handler(message, summa)
        return
    try:
        res = currency.convert(amount, values[0], values[1])
        res_rounded = round(res, 2)
        bot.send_message(message.chat.id, f'Результат: {res_rounded}. Вкажіть сумму для повторної конвертації')
        bot.register_next_step_handler(message, summa)
    except ValueError:
        bot.send_message(message.chat.id, 'Непідтримувана валюта. Виберіть іншу валютну пару')
        bot.register_next_step_handler(message, summa)


@bot.message_handler(commands=['cancel'])
def cancel_convert_mode(message):
    global waiting_for_convert_command
    waiting_for_convert_command = False
    bot.send_message(message.chat.id, 'Вихід з режиму конвертації. Щоб повернутися, введіть /convert')


@bot.message_handler(commands=['commands'], func=lambda message: waiting_for_commands_command)
def show_commands(message):
    global waiting_for_commands_command
    waiting_for_commands_command = False
    commands = [
        "/convert - Запустити конвертатор валют",
        "/crypto - Показати актуальний курс криптовалют",
        "/curse - Показати курси валют"
    ]
    bot.send_message(message.chat.id, "\n".join(commands))


@bot.message_handler(commands=['crypto'])
def show_crypto(message):
    try:
        response = requests.get('https://api.coingecko.com/api/v3/simple/price',
                                params={'ids': 'bitcoin,ethereum,ripple', 'vs_currencies': 'usd'})
        data = response.json()
        crypto_rates = {
            "Bitcoin (BTC)": data['bitcoin']['usd'],
            "Ethereum (ETH)": data['ethereum']['usd'],
            "Ripple (XRP)": data['ripple']['usd']
        }
        response_text = "\n".join([f"{crypto}: ${rate}" for crypto, rate in crypto_rates.items()])
        bot.send_message(message.chat.id, "Курси криптовалют до долара:\n" + response_text)
    except Exception as e:
        bot.send_message(message.chat.id, f'Виникла помилка: {str(e)}')


@bot.message_handler(commands=['curse'])
def show_exchange_rates(message):
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
        data = response.json()

        rates = data['rates']
        base_currency = data['base']

        response_text = "\n".join([f"{currency}: {rate}" for currency, rate in rates.items()])
        bot.send_message(message.chat.id, f"Курси валют відносно {base_currency}:\n" + response_text)
    except Exception as e:
        bot.send_message(message.chat.id, f'Виникла помилка: {str(e)}')


bot.polling(none_stop=True)
