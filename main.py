import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from datetime import datetime
import telebot
from telebot import types
import os


scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Создаем бота
bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
bot.remove_webhook()
bot.set_webhook('d5di8f6lfa7p5kdfb24g.apigw.yandexcloud.net')

# Команда start
@bot.message_handler(commands=["start"])
def start(m, res=False):
    markup=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1=types.KeyboardButton("Я хочу записаться на диагностику")
    item2=types.KeyboardButton("Я хочу получить ссылку на встречу")
    markup.add(item1, item2)
    bot.send_message(m.chat.id, 'Привет, я бот для записи на диагностику-знакомство к Диане Шигаевой. \n\nДиагностика-знакомство длится 20 минут и включает в себя обсуждение: \n- вашей текущей ситуации, \n- какой результат хочется, \n- краткий анализ: где действуете неэффективно/чего не хватает для того, чтобы достичь результат, \n- предложение: какая из наших программ лучше подойдёт, какое наполнение будет оптимальным, описанные этапы, стоимость, длительность. \n\nПеред записью вы можете уже ознакомиться с описанием основных программ, нашей экспертизой и стоимостью здесь - www.DianaShigaeva.ru. \n\nДля записи на диагностику-знакомство нажмите "Я хочу записаться на диагностику". \n\nЕсли вы уже записались и хотите получить ссылку на конференцию, нажмите "Я хочу получить ссылку на встречу". \n\nЕсли в процессе записи у вас появятся проблемы или вопросы, пришлите мне команду /help.', reply_markup=markup)

    
@bot.message_handler(content_types=["text"])
def descide_where(m):
    stages = [get_name, get_topic, get_info, get_cv, get_mail, get_registration]
    wsh = client.open("clients_new").sheet1
    users_list = wsh.col_values(1)
    user_row = 0
    telegram_id = m.from_user.username
    if telegram_id in users_list:
        user_cells = wsh.findall(telegram_id)
        user_row = user_cells[-1].row
    if m.text == "Я хочу записаться на диагностику":
        a = telebot.types.ReplyKeyboardRemove()
        if user_row > 0 and int(wsh.row_values(user_row)[1]) in range(1, 6):
            markup=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            item1=types.KeyboardButton("Продолжить запись")
            item2=types.KeyboardButton("Записаться сначала")
            markup.add(item1, item2)
            bot.send_message(m.chat.id, 'В моей базе сохранился черновик вашей прошлой записи. Вы хотите продолжить запись с шага, на котором остановились, или записаться заново?', reply_markup=markup)
        elif user_row > 0 and int(wsh.row_values(user_row)[1]) == 6:
            markup=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            item1=types.KeyboardButton("Записаться сначала")
            markup.add(item1)
            bot.send_message(m.chat.id, 'Вы уже записались на диагностику! Хотите записаться еще раз?', reply_markup=markup)
        else:
            a = telebot.types.ReplyKeyboardRemove()
            wsh.append_row([telegram_id, 0])
            bot.send_message(m.chat.id, 'Напишите, пожалуйста, как вас зовут (ФИО).', reply_markup=a)
    elif m.text == "Я хочу получить ссылку на встречу":
        if user_row == 0 or user_row > 0 and wsh.row_values(user_row)[6] == '':
            markup=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            item1=types.KeyboardButton("Я хочу записаться на диагностику")
            markup.add(item1)
            bot.send_message(m.chat.id, 'Кажется, вы пока что не записывались на диагностику или не завершили запись. Чтобы это исправить, нажмите "Я хочу записаться на диагностику".', reply_markup=markup)
        else:
            worksheet_read = client.open("events").sheet1
            cell = worksheet_read.find(f"dnshigaeva@gmail.com,{wsh.row_values(user_row)[6]}")
            if cell is None:
                a = telebot.types.ReplyKeyboardRemove()
                bot.send_message(m.chat.id, 'Почему-то у меня не получается найти вашу запись( \n\nПроверьте, что calendly принял вашу запись, а также проверьте корректность введенного email на сайте. Если все правильно, ссылка придет вам на почту.', reply_markup=a)
            else:
                values_list = worksheet_read.row_values(cell.row)
                meet_time = values_list[3]
                link = values_list[4]
                bot.send_message(m.chat.id, f'Диагностика-знакомство пройдет {meet_time} по ссылке {link}.')

    elif m.text == "Записаться сначала":
        a = telebot.types.ReplyKeyboardRemove()
        wsh.append_row([telegram_id, 0])
        bot.send_message(m.chat.id, 'Напишите, пожалуйста, как вас зовут (ФИО).', reply_markup=a)
    elif m.text == 'У меня не получилось записаться':
        wsh.update_cell(user_row, (int(wsh.row_values(user_row)[1]) + 3), m.text)
        markup=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        item1=types.KeyboardButton("Вернуться назад")
        markup.add(item1)
        bot.send_message(m.chat.id, 'Напишите Диане @DianaShigaeva или ее ассистентке Оле @oil_go и объясните ситуацию, они помогут вам записаться.', reply_markup=markup)
    elif m.text == '/start':
        markup=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        item1=types.KeyboardButton("Я хочу записаться на диагностику")
        markup.add(item1)
        bot.send_message(m.chat.id, 'Привет, я бот для записи на диагностику-знакомство к Диане Шигаевой. \n\nДля записи на диагностику-знакомство нажмите "Я хочу записаться на диагностику". \n\nЕсли вы уже записались и хотите получить ссылку на конференцию, нажмите "Я хочу получить ссылку на встречу". \n\nЕсли в процессе записи у вас появятся проблемы или вопросы, пришлите мне команду /help.', reply_markup=markup)
    elif m.text == "Продолжить запись":
        stages[int(wsh.row_values(user_row)[1]) - 1](m)
        wsh.update_cell(user_row, 2, int(wsh.row_values(user_row)[1]))
    elif m.text == "Вернуться назад":
        if int(wsh.row_values(user_row)[1]) == 1:
            a = telebot.types.ReplyKeyboardRemove()
            bot.send_message(m.chat.id, 'Напишите, пожалуйста, как вас зовут (ФИО).', reply_markup=a)
            wsh.update_cell(user_row, 2, 0)
        else:
            stages[int(wsh.row_values(user_row)[1]) - 2](m)
            wsh.update_cell(user_row, 2, int(wsh.row_values(user_row)[1]) - 1)
    elif m.text == '/help':
        markup=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        item1=types.KeyboardButton("Продолжить запись")
        item2=types.KeyboardButton("Записаться сначала")
        markup.add(item1, item2)
        bot.send_message(m.chat.id, 'Если в какой-то момент что-то пошло не так (например, вы отправили мне неправильные данные), можете записаться сначала. Если у вас есть какие-то вопросы, можете написать Диане @DianaShigaeva или ее ассистентке Оле @oil_go', reply_markup=markup)
    elif m.text == "Продолжить запись":
        if int(wsh.row_values(user_row)[1]) == 0:
            a = telebot.types.ReplyKeyboardRemove()
            bot.send_message(m.chat.id, 'Напишите, пожалуйста, как вас зовут (ФИО).', reply_markup=a)
        else:
            stages[int(wsh.row_values(user_row)[1]) - 1](m)
            wsh.update_cell(user_row, 2, int(wsh.row_values(user_row)[1]))
    elif m.text != "Завершить запись":
        if user_row > 0 and int(wsh.row_values(user_row)[1]) < 6:
            wsh.update_cell(user_row, (int(wsh.row_values(user_row)[1]) + 3), m.text)
            stages[int(wsh.row_values(user_row)[1])](m)
            wsh.update_cell(user_row, 2, int(wsh.row_values(user_row)[1]) + 1)
        elif user_row > 0:
            markup=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            item1=types.KeyboardButton("Записаться сначала")
            markup.add(item1)
            bot.send_message(m.chat.id, 'Вы уже записались на диагностику! Хотите записаться еще раз?', reply_markup=markup)
        elif user_row == 0:
            a = telebot.types.ReplyKeyboardRemove()
            bot.send_message(m.chat.id, 'Извините, я вас не понимаю. Если запутались, пришлите мне команду /help.', reply_markup=a)


def get_name(m):
    markup=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1=types.KeyboardButton("Подготовка к релокации")
    item2=types.KeyboardButton("Поиск работы по ценностям")
    item3=types.KeyboardButton("Поиск работы быстро")
    item4=types.KeyboardButton("Создание резюме/профиля на LinkedIn")
    item5=types.KeyboardButton("Подготовка к интервью")
    item6=types.KeyboardButton("Карьерная программа")
    item7=types.KeyboardButton("Вернуться назад")
    markup.add(item1, item2, item3, item4, item5, item6, item7)
    bot.send_message(m.chat.id, 'Выберите актуальную для вас тему.', reply_markup=markup)


def get_topic(m):
    markup=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1=types.KeyboardButton("Вернуться назад")
    markup.add(item1)
    bot.send_message(m.chat.id, 'Опишите, пожалуйста, кратко свою ситуацию: кем работаете, какая сейчас ситуация, основной запрос, какой результат хочется.', reply_markup=markup)


def get_info(m):
    markup=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1=types.KeyboardButton("Вернуться назад")
    markup.add(item1)
    bot.send_message(m.chat.id, 'Пришлите ссылку на ваш профиль на LinkedIn (либо на резюме).', reply_markup=markup)


def get_cv(m):
    markup=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1=types.KeyboardButton("Вернуться назад")
    markup.add(item1)
    bot.send_message(m.chat.id, 'Пришлите ваш email.', reply_markup=markup)


def get_mail(m):
    markup=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1=types.KeyboardButton('Я выбрал время и записался')
    item2=types.KeyboardButton('У меня не получилось записаться')
    item3=types.KeyboardButton("Вернуться назад")
    markup.add(item1, item2, item3)
    bot.send_message(m.chat.id, 'Вы можете выбрать время созвона вот тут: https://calendly.com/dianashigaeva. \n\nПри записи напишите в поле Name "Диагностика + имя фамилия" и укажите свой адрес электронной почты в поле Email.', reply_markup=markup)

def get_registration(m):
    markup=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1=types.KeyboardButton("Завершить запись")
    item2=types.KeyboardButton("Вернуться назад")
    markup.add(item1, item2)
    bot.send_message(m.chat.id, 'Отлично, я все записал! Нажмите "Завершить запись". Ссылка на видеоконференцию придет к вам на почту, но вы можете и попросить ее у меня за какое-то время до встречи. Для этого напишите /start и выберите вариант "Я хочу получить ссылку на встречу".', reply_markup=markup)


if __name__ == '__main__':
    bot.enable_save_next_step_handlers(delay=1)
    bot.load_next_step_handlers()
    bot.infinity_polling(timeout=10, long_polling_timeout = 5)

