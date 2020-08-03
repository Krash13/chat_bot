# - *- coding: utf- 8 - *-
import MySQLdb
import telebot
import random
import requests
from geopy.geocoders import Nominatim
import constants

bot=telebot.TeleBot(constants.token)
conn = MySQLdb.connect(constants.host, constants.user, constants.passw, constants.db,charset='utf8')
keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard2 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard3 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard4 = telebot.types.ReplyKeyboardMarkup(True, True)
remkeyb=telebot.types.ReplyKeyboardRemove()
keyboard1.row('М', 'Ж')
keyboard2.row('М', 'Ж', "Всё равно")
keyboard3.row('16-18', '18-23','23-30').add('30-40','40-55','55+')
keyboard3.add('Всё равно')
keyboard4.row('Общение', 'Дружба').add('Отношения','Секс')
keyboard4.add('Всё равно')

keyboard_geo = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
button_geo = telebot.types.KeyboardButton(text="Отправить местоположение", request_location=True)
keyboard_geo.add(button_geo)

@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, '/start - запуск бота\n/search - поиск собеседник\n/search_all - поиск без параметров\n/next - смена собеседника\n/stop - остановить поиск\n/update_info - обновить данные о себе\n/update_target - обновить критерии поиска\n/delete_anket - удалить анкету\n/help - помощь')

@bot.message_handler(commands=['start'])
def start_message(message):
    conn = MySQLdb.connect(constants.host, constants.user, constants.passw, constants.db, charset='utf8')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id={}".format(message.chat.id))
    row = cursor.fetchone()
    if row==None:
        cursor.execute("INSERT INTO users (user_id,status) VALUES ({},0)".format(message.chat.id))
        bot.send_message(message.chat.id, 'Привет, как мне тебя называть?')
    print(message.chat)
    conn.close()
@bot.message_handler(commands=['search_all'])
def search_all_message(message):
    conn = MySQLdb.connect(constants.host, constants.user, constants.passw, constants.db, charset='utf8')
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM users WHERE user_id={}".format(message.chat.id))
    row = cursor.fetchone()
    if row!=None and row[0]==8:
        bot.send_message(message.chat.id, 'Ожидайте собеседника...')
        cursor.execute("UPDATE users SET searching=2, companion=NULL WHERE user_id={}".format(message.chat.id))
        cursor.execute("SELECT user_id FROM users WHERE user_id<>{} AND searching=2".format(message.chat.id))
        rows=cursor.fetchall()
        #print(rows)
        if len(rows):
            index = random.randint(0, len(rows) - 1)
            id = rows[index][0]
            cursor.execute("UPDATE users SET searching=1, companion={} WHERE user_id={}".format(id, message.chat.id))
            cursor.execute("UPDATE users SET searching=1, companion={} WHERE user_id={}".format(message.chat.id, id))
            bot.send_message(message.chat.id,'Собеседник найден! \n /stop - остановить диалог')
            bot.send_message(id, 'Собеседник найден! \n /stop - остановить диалог')
    else:
        bot.send_message(message.chat.id,'Ваша анкета ещё не заполнена!')
    conn.close()

@bot.message_handler(commands=['search'])
def search_message(message):
    conn = MySQLdb.connect(constants.host, constants.user, constants.passw, constants.db, charset='utf8')
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM users WHERE user_id={}".format(message.chat.id))
    row = cursor.fetchone()
    if row!=None and row[0]==8:
        bot.send_message(message.chat.id, 'Ожидайте собеседника... \nЕсли собеседник долго не находится, попробуйте команду:\n /search_all - поиск без параметром')
        request="SELECT users.user_id FROM users, search WHERE"
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET searching=0, companion=NULL WHERE user_id={}".format(message.chat.id))
        cursor.execute("SELECT * FROM search WHERE user_id={}".format(message.chat.id))
        row1 = cursor.fetchone()
        cursor.execute("SELECT * FROM users WHERE user_id={}".format(message.chat.id))
        row2 = cursor.fetchone()
        request+=" users.age>={} AND users.age<={}".format(row1[3],row1[4])
        if row1[2]!=None:
            request += " AND users.gender='{}'".format(row1[2])

        if row1[5]!=None:
            request += " AND users.city='{}'".format(row1[5])

        if row1[6]!=None:
            request += " AND (search.target='{}' OR search.target IS NULL)".format(row1[6])

        request += " AND (search.gender='{}' OR search.gender IS NULL)".format(row2[2])
        if row1[6]!=None:
            request += " AND (search.target='{}' OR search.target IS NULL)".format(row1[6])
        request += " AND (search.city='{}' OR search.city IS NULL)".format(row2[4])
        request += " AND search.age_min<={} AND search.age_max>={}".format(row2[3],row2[3])
        request+=" AND users.user_id<>{}".format(message.chat.id)
        request += " AND users.searching=0"
        request += " AND users.user_id=search.user_id"
        print(request)
        cursor.execute(request)
        row = cursor.fetchone()
        print(row)
        ids=[]
        while row!=None:
            ids.append(row[0])
            row = cursor.fetchone()

        if len(ids)>0:
            index=random.randint(0,len(ids)-1)
            id=ids[index]
            cursor.execute("UPDATE users SET searching=1, companion={} WHERE user_id={}".format(id,message.chat.id))
            cursor.execute("UPDATE users SET searching=1, companion={} WHERE user_id={}".format(message.chat.id,id))
            bot.send_message(message.chat.id, 'Собеседник найден! \n /next - сменить собеседника \n /stop - остановить диалог')
            bot.send_message(id, 'Собеседник найден! \n /next - сменить собеседника \n /stop - остановить диалог')
    else:
        bot.send_message(message.chat.id,'Ваша анкета ещё не заполнена!')
    conn.close()

@bot.message_handler(commands=['next'])
def next_message(message):
    conn = MySQLdb.connect(constants.host, constants.user, constants.passw, constants.db, charset='utf8')
    cursor = conn.cursor()
    cursor.execute('SELECT companion FROM users WHERE user_id={}'.format(message.chat.id))
    row = cursor.fetchone()
    cursor.execute("SELECT status FROM users WHERE user_id={}".format(message.chat.id))
    row1 = cursor.fetchone()
    if row!=None and row[0]!=None and row1[0]==8:
        id=row[0]
        cursor.execute("UPDATE users SET searching=NULL, companion=NULL WHERE user_id={}".format(message.chat.id))
        cursor.execute("UPDATE users SET searching=NULL, companion=NULL WHERE user_id={}".format(id))
        bot.send_message(id, 'Собеседник остановил диалог... Для поиска используйте /search')
        search_message(message)
    else:
        bot.send_message(message.chat.id, 'Нажмите /search для поиска')
    conn.close()


@bot.message_handler(commands=['stop'])
def stop_message(message):
    conn = MySQLdb.connect(constants.host, constants.user, constants.passw, constants.db, charset='utf8')
    cursor = conn.cursor()
    cursor.execute('SELECT companion FROM users WHERE user_id={}'.format(message.chat.id))
    row = cursor.fetchone()
    cursor.execute("UPDATE users SET searching=NULL, companion=NULL WHERE user_id={}".format(message.chat.id))
    bot.send_message(message.chat.id, 'Для поиска используйте /search')
    if row!=None and row[0] != None:
        id=row[0]
        cursor.execute("UPDATE users SET searching=NULL, companion=NULL WHERE user_id={}".format(id))
        bot.send_message(id, 'Собеседник остановил диалог... Для поиска используйте /search')
    conn.close()

@bot.message_handler(commands=['update_info'])
def next_message(message):
    conn = MySQLdb.connect(constants.host, constants.user, constants.passw, constants.db, charset='utf8')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id={}".format(message.chat.id))
    row = cursor.fetchone()
    if row!=None:
        cursor.execute("UPDATE users SET status=0, searching=NULL WHERE user_id={}".format(message.chat.id))
        bot.send_message(message.chat.id, 'Привет, как мне тебя называть?')
    conn.close()

@bot.message_handler(commands=['update_target'])
def next_message(message):
    conn = MySQLdb.connect(constants.host, constants.user, constants.passw, constants.db, charset='utf8')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM search WHERE user_id={}".format(message.chat.id))
    row = cursor.fetchone()
    if row!=None:
        cursor.execute("UPDATE users SET status=4, searching=NULL WHERE user_id={}".format(message.chat.id))
        cursor.execute("UPDATE search SET gender=NULL, age_min=NULL, age_max=NULL, city=NULL, target=NULL WHERE user_id={}".format(message.chat.id))
        bot.send_message(message.chat.id, 'Теперь разбеёмсся кого вы ищете!', reply_markup=keyboard2)
    conn.close()

@bot.message_handler(commands=['delete_anket'])
def delete_message(message):
    conn = MySQLdb.connect(constants.host, constants.user, constants.passw, constants.db, charset='utf8')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM search WHERE user_id={}".format(message.chat.id))
    cursor.execute("DELETE FROM users WHERE user_id={}".format(message.chat.id))
    bot.send_message(message.chat.id, 'Чтобы венуться к нам нажмите /start')
    conn.close()

@bot.message_handler(content_types=['text'])
def send_text(message):
    conn = MySQLdb.connect(constants.host, constants.user, constants.passw, constants.db, charset='utf8')
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM users WHERE user_id={}".format(message.chat.id))
    status = cursor.fetchone()
    if status==None:
        conn.close()
        return
    if status[0]==0:
        cursor.execute('UPDATE users SET user_name="{}", status=status+1 WHERE user_id={}'.format(message.text ,message.chat.id))
        bot.send_message(message.chat.id, 'Сколько тебе лет?')
    elif status[0] == 1:
        if message.text.isdigit() and int(message.text)<99:
            cursor.execute('UPDATE users SET age={}, status=status+1 WHERE user_id={}'.format(message.text ,message.chat.id))
            bot.send_message(message.chat.id, 'Кто ты?', reply_markup=keyboard1)
        else:
            bot.send_message(message.chat.id, 'Сколько тебе лет?')
    elif status[0] == 2:
        if message.text in ('М', 'Ж'):
            cursor.execute('UPDATE users SET gender="{}", status=status+1 WHERE user_id={}'.format(message.text ,message.chat.id))
            bot.send_message(message.chat.id, 'Из какого ты города? напиши или нажми кнопку.',reply_markup=keyboard_geo)
        else:
            bot.send_message(message.chat.id, 'Кто ты?', reply_markup=keyboard1)
    elif status[0] == 3:
        cursor.execute('UPDATE users SET city="{}", status=status+1 WHERE user_id={}'.format(message.text, message.chat.id))
        #bot.send_message(message.chat.id, 'Теперь разбеёмсся кого вы ищете!',reply_markup=keyboard2)
        cursor.execute("SELECT user_id FROM search WHERE user_id={}".format(message.chat.id))
        #print("SELECT user_id FROM search WHERE user_id={}".format(message.chat.id))
        row = cursor.fetchone()
        if row != None:
            cursor.execute('UPDATE users SET status=8 WHERE user_id={}'.format(message.chat.id))
            bot.send_message(message.chat.id, 'Отлично, можно начинать! Для поиска введите /search',reply_markup=remkeyb)
        else:
            bot.send_message(message.chat.id, 'Теперь разбеёмсся кого вы ищете!', reply_markup=keyboard2)
    elif status[0] == 4:
        if message.text in ('М', 'Ж', "Всё равно"):
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM search WHERE user_id={}".format(message.chat.id))
            row = cursor.fetchone()
            if row == None:
                cursor.execute("INSERT INTO search (user_id) VALUES ({})".format(message.chat.id))
            if message.text!='Всё равно':
                cursor.execute('UPDATE search SET gender="{}" WHERE user_id={}'.format(message.text,message.chat.id))
            cursor.execute('UPDATE users SET  status=status+1 WHERE user_id={}'.format(message.chat.id))
            bot.send_message(message.chat.id, 'Теперь разберёмся с возрастом', reply_markup=keyboard3)
        else:
            bot.send_message(message.chat.id, 'Теперь разбеёмсся кого вы ищете!', reply_markup=keyboard2)
    elif status[0] == 5:
        if message.text in ('16-18', '18-23','23-30','30-40','40-55','55+', "Всё равно"):
            if message.text != 'Всё равно' and message.text != '55+':
                text=message.text.split("-")
                cursor.execute('UPDATE search SET age_min={}, age_max={} WHERE user_id={}'.format(text[0],text[1], message.chat.id))
            elif message.text == '55+':
                cursor.execute('UPDATE search SET age_min=55, age_max=99 WHERE user_id={}'.format(message.chat.id))
            else:
                cursor.execute('UPDATE search SET age_min=0, age_max=99 WHERE user_id={}'.format(message.chat.id))
            cursor.execute('UPDATE users SET  status=status+1 WHERE user_id={}'.format(message.chat.id))
            bot.send_message(message.chat.id, 'Из какого города? Если вам всё равно отправьте "."', reply_markup=remkeyb)
        else:
            bot.send_message(message.chat.id, 'Теперь разберёмся с возрастом', reply_markup=keyboard3)
    elif status[0] == 6:
        if message.text!=".":
            cursor.execute('UPDATE search SET city="{}" WHERE user_id={}'.format(message.text, message.chat.id))
        cursor.execute('UPDATE users SET  status=status+1 WHERE user_id={}'.format(message.chat.id))
        bot.send_message(message.chat.id, 'Для чего вы тут?', reply_markup=keyboard4)
    elif status[0]==7:
        if message.text in ('Общение', 'Дружба','Отношения','Секс', "Всё равно"):
            if message.text != 'Всё равно':
                cursor.execute('UPDATE search SET target="{}" WHERE user_id={}'.format(message.text, message.chat.id))
            cursor.execute('UPDATE users SET  status=status+1 WHERE user_id={}'.format(message.chat.id))
            bot.send_message(message.chat.id, 'Отлично, можно начинать! Для поиска введите /search', reply_markup=remkeyb)
        else:
            bot.send_message(message.chat.id, 'Для чего вы тут?', reply_markup=keyboard4)
    elif status[0] == 8:
        cursor.execute('SELECT companion FROM users WHERE user_id={}'.format(message.chat.id))
        row=cursor.fetchone()
        if row[0]!=None:
            bot.send_message(row[0], message.text)
    conn.close()

@bot.message_handler(content_types=['photo'])
def send_text(message):
    conn = MySQLdb.connect(constants.host, constants.user, constants.passw, constants.db, charset='utf8')
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM users WHERE user_id={}".format(message.chat.id))
    status = cursor.fetchone()
    if status == None:
        return
    if status[0] == 8:
        cursor.execute('SELECT companion FROM users WHERE user_id={}'.format(message.chat.id))
        row=cursor.fetchone()
        if row[0]!=None:
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            bot.send_photo(row[0], downloaded_file, message.caption)
    conn.close()

@bot.message_handler(content_types=["location"])
def location(message):
    if message.location is not None:
        conn = MySQLdb.connect(constants.host, constants.user, constants.passw, constants.db, charset='utf8')
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM users WHERE user_id={}".format(message.chat.id))
        status = cursor.fetchone()
        if status == None:
            conn.close()
            return
        elif status[0] == 3:
            geolocator = Nominatim(user_agent="bisnesteleg12@gmail.com")
            location = geolocator.reverse("{}, {}".format(message.location.latitude,message.location.longitude),language="ru")
            if "city" in location.raw['address']:
                loc=location.raw['address']['city']
            elif "village" in location.raw['address']:
                loc=location.raw['address']['village']
            else:
                bot.send_message(message.chat.id, 'Ваш город не найден введите текстом...',reply_markup=remkeyb)
                conn.close()
                return
            cursor.execute('UPDATE users SET city="{}", status=status+1 WHERE user_id={}'.format(loc, message.chat.id))
            cursor.execute("SELECT user_id FROM search WHERE user_id={}".format(message.chat.id))
            row = cursor.fetchone()
            if row != None:
                cursor.execute('UPDATE users SET status=8 WHERE user_id={}'.format(message.chat.id))
                bot.send_message(message.chat.id, 'Отлично, можно начинать! Для поиска введите /search',reply_markup=remkeyb)
            else:
                bot.send_message(message.chat.id, 'Теперь разбеёмсся кого вы ищете!', reply_markup=keyboard2)
            conn.close()

@bot.message_handler(content_types=["sticker"])
def send_sticker(message):
    conn = MySQLdb.connect(constants.host, constants.user, constants.passw, constants.db, charset='utf8')
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM users WHERE user_id={}".format(message.chat.id))
    status = cursor.fetchone()
    if status == None:
        conn.close()
        return
    elif status[0] == 8:
        cursor.execute('SELECT companion FROM users WHERE user_id={}'.format(message.chat.id))
        row = cursor.fetchone()
        if row[0] != None:
            bot.send_sticker(row[0],message.sticker.file_id)
    conn.close()

@bot.message_handler(content_types=["voice"])
def send_audio(message):
    conn = MySQLdb.connect(constants.host, constants.user, constants.passw, constants.db, charset='utf8')
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM users WHERE user_id={}".format(message.chat.id))
    status = cursor.fetchone()
    if status == None:
        return
    if status[0] == 8:
        cursor.execute('SELECT companion FROM users WHERE user_id={}'.format(message.chat.id))
        row = cursor.fetchone()
        if row[0] != None:
            file_info = bot.get_file(message.voice.file_id)
            file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(constants.token, file_info.file_path))
            bot.send_voice(row[0],file.content)
    conn.close()

bot.polling(none_stop=True)
conn.close()

