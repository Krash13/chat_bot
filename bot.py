import MySQLdb
import telebot
import random
import constants
bot=telebot.TeleBot(constants.token)

conn = MySQLdb.connect('localhost', 'root', '', 'chat_bot',charset='utf8')
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

@bot.message_handler(commands=['start'])
def start_message(message):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id={}".format(message.chat.id))
    row = cursor.fetchone()
    if row==None:
        cursor.execute("INSERT INTO users (user_id,status) VALUES ({},0)".format(message.chat.id))
        bot.send_message(message.chat.id, 'Привет, как мне тебя называть?')
    print(message.chat)

@bot.message_handler(commands=['search'])
def search_message(message):
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM users WHERE user_id={}".format(message.chat.id))
    row = cursor.fetchone()
    if row[0]==8:
        bot.send_message(message.chat.id, 'Ожидайте собеседника...')
        request="SELECT users.user_id FROM users, search WHERE"
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET searching=0 WHERE user_id={}".format(message.chat.id))
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
            request += " AND search.target='{}'".format(row1[6])

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

@bot.message_handler(commands=['next'])
def next_message(message):
    cursor = conn.cursor()
    cursor.execute('SELECT companion FROM users WHERE user_id={}'.format(message.chat.id))
    row = cursor.fetchone()
    if row[0]!=None:
        id=row[0]
        cursor.execute("UPDATE users SET searching=NULL, companion=NULL WHERE user_id={}".format(message.chat.id))
        cursor.execute("UPDATE users SET searching=NULL, companion=NULL WHERE user_id={}".format(id))
        bot.send_message(id, 'Собеседник остановил диалог... Для поиска используйте /search')
        search_message(message)
    else:
        bot.send_message(message.chat.id, 'Нажмите /search для поиска')


@bot.message_handler(commands=['stop'])
def stop_message(message):
    cursor = conn.cursor()
    cursor.execute('SELECT companion FROM users WHERE user_id={}'.format(message.chat.id))
    row = cursor.fetchone()
    id=row[0]
    cursor.execute("UPDATE users SET searching=NULL, companion=NULL WHERE user_id={}".format(message.chat.id))
    cursor.execute("UPDATE users SET searching=NULL, companion=NULL WHERE user_id={}".format(id))
    bot.send_message(message.chat.id, 'Для поиска используйте /search')
    bot.send_message(id, 'Собеседник остановил диалог... Для поиска используйте /search')


@bot.message_handler(content_types=['text'])
def send_text(message):
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM users WHERE user_id={}".format(message.chat.id))
    status = cursor.fetchone()
    if status[0]==0:
        cursor.execute('UPDATE users SET user_name="{}", status=status+1 WHERE user_id={}'.format(message.text ,message.chat.id))
        bot.send_message(message.chat.id, 'Сколько тебе лет?')
    elif status[0] == 1:
        if int(message.text)<99:
            cursor.execute('UPDATE users SET age={}, status=status+1 WHERE user_id={}'.format(message.text ,message.chat.id))
            bot.send_message(message.chat.id, 'Кто ты?', reply_markup=keyboard1)
        else:
            bot.send_message(message.chat.id, 'Сколько тебе лет?')
    elif status[0] == 2:
        if message.text in ('М', 'Ж'):
            cursor.execute('UPDATE users SET gender="{}", status=status+1 WHERE user_id={}'.format(message.text ,message.chat.id))
            bot.send_message(message.chat.id, 'Из какого ты города?',reply_markup=remkeyb)
        else:
            bot.send_message(message.chat.id, 'Кто ты?', reply_markup=keyboard1)
    elif status[0] == 3:
        cursor.execute('UPDATE users SET city="{}", status=status+1 WHERE user_id={}'.format(message.text, message.chat.id))
        #bot.send_message(message.chat.id, 'Теперь разбеёмсся кого вы ищете!',reply_markup=keyboard2)
        cursor.execute("SELECT user_id FROM search WHERE user_id={}".format(message.chat.id))
        print("SELECT user_id FROM search WHERE user_id={}".format(message.chat.id))
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
        bot.send_message(row[0], message.text)

bot.polling()
conn.close()

