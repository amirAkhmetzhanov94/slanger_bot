from telebot import types
from telebot.apihelper import ApiException
import config
import telebot
import requests
from bs4 import BeautifulSoup
from googletrans import Translator


bot = telebot.TeleBot(config.TOKEN, parse_mode="html")


@bot.message_handler(commands=["start"])
def helping(message):
    bot.send_message(message.chat.id, """
    Привет, меня зовут сленгербот. Я помогу тебе понять значения некоторых английских жаргонов. 
    
    • Чтобы запустить меня, пропиши /launch. 
    
    • Если нашёл какой-то баг, долби разраба в личку: @kurzwei777. 
    
    • Если кнопки с выбором языка - пропали, пожалуйста нажми на кнопочку, показанную на скриншоте ниже. 
    
    Приятного тебе юзер-экспериенса :)""")
    bot.send_photo(message.chat.id, 'https://i.ibb.co/N33r9wy/photo5222236343227232739.jpg')


@bot.message_handler(commands=["launch"])
def starting_program(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    button_english = types.KeyboardButton(text="English 🇺🇸")
    button_russian = types.KeyboardButton(text="Русский 🇷🇺")
    keyboard.add(button_english, button_russian)
    bot.send_message(message.chat.id, "На каком языке хочешь получить пояснение по слову/фразе?",
                     reply_markup=keyboard)


@bot.message_handler(content_types=["text"])
def selecting_language(message):
    if message.text == "English 🇺🇸":
        message = bot.send_message(message.chat.id, "Write your phrase or word: ")
        bot.register_next_step_handler(message, slanger_function_eng)
    elif message.text == "Русский 🇷🇺":
        message = bot.send_message(message.chat.id, "Напиши свою фразу или слово: ")
        bot.register_next_step_handler(message, slanger_function_rus)


@bot.message_handler(content_types=["text"])
def slanger_function_rus(message):
    translate = Translator()
    get_message = message.text.strip().lower()
    set_param = {'term': get_message}
    url = "https://www.urbandictionary.com/define.php"
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.191',
        'accept': '*/*'}
    html = requests.get(url, headers=headers, params=set_param)
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, "lxml")
        meaning = soup.select('div .meaning')[0].text
        example = soup.select('div .example')[0].text
        translation_of_meaning = translate.translate(meaning, dest="ru").text
        translation_of_example = translate.translate(example, dest="ru").text
        try:
            bot.send_message(message.chat.id, "<b>Обозначение</b>:\n" + translation_of_meaning)
        except ApiException:
            bot.send_message(message.chat.id,
                             'Обозначение данного слова - слишком длинное, попробуйте посмотреть на сайте: '
                             'https://translate.google.com/translate?hl=en&sl=auto&tl=ru&u=https%3A%2F%2Fwww'
                             f'.urbandictionary.com%2Fdefine.php%3Fterm%3D{get_message}&sandbox=1')
        if len(translation_of_example) > 0:
            bot.send_message(message.chat.id, "<b>Пример</b>:\n" + translation_of_example)
        else:
            bot.send_message(message.chat.id, "<b>Пример</b>:\n" + 'Здесь нет примера')
    else:
        bot.send_message(message.chat.id, "Данного слова нет в базе 🙁")
    returning_keyboard_rus = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    button_da = types.KeyboardButton(text="Да")
    button_net = types.KeyboardButton(text="Нет")
    returning_keyboard_rus.add(button_da, button_net)
    bot.send_message(message.chat.id, "<i>Будем переводить что-то ещё?</i>",
                     reply_markup=returning_keyboard_rus)
    bot.register_next_step_handler(message, returning_back)


@bot.message_handler(content_types=["text"])
def slanger_function_eng(message):
    get_message = message.text.strip().lower()
    set_param = {'term': get_message}
    url = "https://www.urbandictionary.com/define.php"
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.191',
        'accept': '*/*'}
    html = requests.get(url, headers=headers, params=set_param)
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, "lxml")
        meaning = soup.select('div .meaning')[0].text
        example = soup.select('div .example')[0].text
        try:
            bot.send_message(message.chat.id, "<b>Definition</b>:\n" + meaning)
        except ApiException:
            bot.send_message(message.chat.id,
                             'The definition is too long, check the website: '
                             'https://www.urbandictionary.com/define.php?term=' + get_message)
        if len(example) > 0:
            bot.send_message(message.chat.id, "<b>Example</b>:\n" + example)
        else:
            bot.send_message(message.chat.id, "<b>Example</b>:\n" + 'There\'s no example')
    else:
        bot.send_message(message.chat.id, "No such word/phrase in database 🙁")
    returning_keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    button_yes = types.KeyboardButton(text="Yes")
    button_no = types.KeyboardButton(text="No")
    returning_keyboard.add(button_yes, button_no)
    bot.send_message(message.chat.id, "<i>Do you wanna translate something else?</i>",
                     reply_markup=returning_keyboard)
    bot.register_next_step_handler(message, returning_back)


@bot.message_handler(content_types=["text"])
def returning_back(message):
    if message.text == "Yes":
        bot.send_message(message.chat.id, "Okay, returning back")
        starting_program(message)
    elif message.text == "No":
        bot.send_message(message.chat.id, """See you soon, cuz 

To start me again, 
just type /launch.

To get some help, 
just type /start.""")
    elif message.text == "Да":
        bot.send_message(message.chat.id, "Хорошо, возвращаемся назад")
        starting_program(message)
    elif message.text == "Нет":
        bot.send_message(message.chat.id, """Увидимся, браза 

Чтобы запустить меня снова, 
пропиши /launch

Чтобы получить инфу по боту, 
пропиши /start""")


if __name__ == '__main__':
    bot.infinity_polling()
