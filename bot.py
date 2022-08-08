import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import telebot
from telebot import types


scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("mypython-356819-6add63778bc2.json", scope)
client = gspread.authorize(creds)

# Создаем бота
bot = telebot.TeleBot('5574285083:AAHK7h8ek-G0haQMG9uzuPlQFNOms--Xn30')
# Команда start
@bot.message_handler(commands=["start"])
def start(m, res=False):
    markup=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1=types.KeyboardButton("Я готов записаться.")
    markup.add(item1)
    bot.send_message(m.chat.id, 'Привет, я бот для записи на диагностику-знакомство к Диане Шигаевой. Перед записью вы можете уже ознакомиться с описанием основных программ, нашей экспертизой и стоимостью здесь - www.DianaShigaeva.ru', reply_markup=markup)

@bot.message_handler(content_types=["text"])
def get_start(m):
    a = telebot.types.ReplyKeyboardRemove()
    if m.text == "Я готов записаться.":
        bot.send_message(m.chat.id, 'Отлично! Напишите, пожалуйста, как вас зовут (ФИО).', reply_markup=a)
        bot.register_next_step_handler(m, get_name)

def get_name(m):
    global name
    name = m.text
    markup=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1=types.KeyboardButton("Подготовка к релокации")
    item2=types.KeyboardButton("Поиск работы по ценностям")
    item3=types.KeyboardButton("Поиск работы быстро")
    item4=types.KeyboardButton("Создание резюме/профиля на LinkedIn")
    item5=types.KeyboardButton("Подготовка к интервью")
    item6=types.KeyboardButton("Карьерная программа")
    markup.add(item1, item2, item3, item4, item5, item6)
    bot.send_message(m.chat.id, 'Выберите актуальную для вас тему.', reply_markup=markup)
    bot.register_next_step_handler(m, get_topic)

def get_topic(m):
    global consultation_type
    consultation_type = m.text
    a = telebot.types.ReplyKeyboardRemove()
    bot.send_message(m.chat.id, 'Опишите, пожалуйста, кратко свою ситуацию: кем работаете, какая сейчас ситуация, основной запрос, какой результат хочется.', reply_markup=a)
    bot.register_next_step_handler(m, get_info)

def get_info(m):
    global user_information
    user_information = m.text
    bot.send_message(m.chat.id, 'Пришлите ссылку на ваш профиль на LinkedIn (либо на резюме).')
    bot.register_next_step_handler(m, get_cv)
    
def get_cv(m):
    global linkedin_link
    linkedin_link = m.text
    markup=types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1=types.KeyboardButton("Я выбрал время и записался.")
    markup.add(item1)
    bot.send_message(m.chat.id, 'Вы можете выбрать время созвона вот тут: https://calendly.com/dianashigaeva', reply_markup=markup)
    bot.register_next_step_handler(m, registered)

def registered(m):
    a = telebot.types.ReplyKeyboardRemove()
    bot.send_message(m.chat.id, 'Пришлите ваш email', reply_markup=a)
    bot.register_next_step_handler(m, get_mail)

def get_mail(m):
    global mail
    mail = m.text
    telegram_id = m.from_user.username
    worksheet_read = client.open("events").sheet1
    bot.send_message(m.chat.id, 'Отлично, я все записал! Скоро пришлю сюда ссылку на созвон.')
    cell = zdun(worksheet_read, mail)
    print(cell)
    values_list = worksheet_read.row_values(cell.row)
    meet_time = values_list[3]
    link = values_list[4]
    bot.send_message(m.chat.id, f'Диагностика-знакомство пройдет {meet_time} по ссылке {link}.')
    worksheet_write = client.open("clients").sheet1
    worksheet_write.append_row([name, consultation_type, user_information, linkedin_link, mail, meet_time, link, telegram_id])

def zdun(wsh, s):
    try:
      a = wsh.find(f"dnshigaeva@gmail.com,{s}")
    except:
      time.sleep(30)
      a = zdun(wsh, s)
    return a

#bot.polling(non_stop=True, interval=0)