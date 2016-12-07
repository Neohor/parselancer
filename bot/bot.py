# -*- coding: utf-8 -*-

from db import *
import telebot
import config

bot = telebot.TeleBot(config.token)
from sqlalchemy.orm import sessionmaker, scoped_session
# Session = sessionmaker(bind=engine)
# session = Session()
session = scoped_session(sessionmaker(bind=engine))

print("Started")

# Обработчик команд '/start' и '/help'.
@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    start_text = 'hello\nsay /list for site list'
    bot.send_message(message.chat.id, start_text)

@bot.message_handler(commands=['wrk', 'list', 'cmd'])
def handle_list(message):
    text = '\U0001f1f7\U0001f1fa /freelansim -- Last job from freelansim.ru\n'+\
           '\U0001f1fa\U0001f1f8 /freelancecom -- Last job from freelance.com'
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['freelancecom', 'fc'])
def handle_freelancecom(message):
    output = '\u2328 /freelance_adm - Last jobs for sysadmins\n'+\
             '\u2692 /freelance_webdev - Last jobs for Web Developers\n'+\
             '\U0001f307 /freelance_webdis - Last jobs for Web Designers\n'+\
             '\U0001f6e0 /freelance_dev - Last jobs for Developers'
    bot.send_message(message.chat.id, output)

@bot.message_handler(commands=['freelansim', 'fr'])
def handle_freelansim(message):
    output = '\u2328 /freelansim_adm - Last jobs for sysadmins\n'+\
             '\u2692 /freelansim_webdev - Last jobs for Web Developers\n'+\
             '\U0001f307 /freelansim_webdis - Last jobs for Web Designers\n'+\
             '\U0001f6e0 /freelansim_dev - Last jobs for Developers'
    bot.send_message(message.chat.id, output)

@bot.message_handler(commands=['freelansim_adm', 'fra'])
def handle_freelansim_adm(message):
    fetch_send_jobs('freelansim', 'admin', message.chat.id)

    output = 'You can subscribe for updates in this category by /subscribe_adm'
    bot.send_message(message.chat.id, output)


@bot.message_handler(commands=['freelansim_webdev', 'frw'])
def handle_freelansim_webdev(message):
    fetch_send_jobs('freelansim', 'webdev', message.chat.id)

@bot.message_handler(commands=['freelansim_webdis', 'frwd'])
def handle_freelansim_webdis(message):
    fetch_send_jobs('freelansim', 'webdis', message.chat.id)

@bot.message_handler(commands=['freelansim_dev', 'frd'])
def handle_freelansim_dev(message):
    fetch_send_jobs('freelansim', 'dev', message.chat.id)


@bot.message_handler(commands=['freelance_adm', 'fca'])
def handle_freelansim_adm(message):
    fetch_send_jobs('freelance', 'admin', message.chat.id)

    output = 'You can subscribe for updates in this category by /subscribe_adm'
    bot.send_message(message.chat.id, output)

@bot.message_handler(commands=['freelance_webdev', 'fcw'])
def handle_freelance_webdev(message):
    fetch_send_jobs('freelance', 'webdev', message.chat.id)

@bot.message_handler(commands=['freelance_webdis', 'fcwd'])
def handle_freelance_webdis(message):
    fetch_send_jobs('freelance', 'webdis', message.chat.id)

@bot.message_handler(commands=['freelance_dev', 'fcd'])
def handle_freelance_dev(message):
    fetch_send_jobs('freelance', 'dev', message.chat.id)


@bot.message_handler(commands=['subscribe_adm', 'sa'])
def handle_freelansim_adm_subscribe(message):
    # if user doesn't exist
    if not user_exist(message.from_user.id):
        # can add new subscription
        user_row = User(name=message.from_user.username,
                        tele_id=message.from_user.id,
                        last_job=get_last_job('admin'),
                        category='admin')
        session.add(user_row)
        session.commit()
    else: # else can update existing subscription
        sql = "UPDATE users SET last_job = '{}', category = '{}' \
               WHERE tele_id = '{}'".format(get_last_job('admin'), 'admin', message.from_user.id)
        session.execute(sql)
        session.commit()

    output = 'Chat ID: ' + str(message.chat.id) + \
             '\nUser ID: ' + str(message.from_user.id) + \
             '\nNick: ' + str(message.from_user.username) + \
             '\nLast JOB ID in this category: ' + str(get_last_job('admin')) + \
             '\nYou subscribed on Administration category'
    bot.send_message(message.chat.id, output)

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):  # Название функции не играет никакой роли, в принципе
    print(message.chat.id)
    print(message)
    if not message.chat.id == config.freelance_chan_id:
        text = str(message.chat.id) + '\n' + message.text
        bot.send_message(message.chat.id, text)

#####################################################################
def user_exist(user_id):
    cur = session.execute("SELECT id FROM users WHERE tele_id = '{}'".format(user_id))
    try:
        output = 'Checked ID: {} \
                 \nExisted User ID: {} \
                 \n__DEBUG__ _MESSAGE_'.format(user_id, cur.fetchone()[0])
        bot.send_message(user_id, output)
        return True
    except TypeError: # if not in DB
        return False

def get_last_job(category):
    cur = session.execute("SELECT id \
                           FROM job \
                           WHERE category = '{}' \
                           ORDER BY id DESC \
                           LIMIT 1".format(category))
    return cur.fetchone()[0]

def fetch_send_jobs(site, category, user_id):
    cur = session.execute("SELECT * \
                           FROM job \
                           WHERE url like '%{}%' \
                           AND category = '{}' \
                           ORDER BY id \
                           DESC LIMIT {}".format(site, category, 3))
    jobs = cur.fetchall()
    for job in jobs:
        output = str(job.id) + ' ' + job[4] + \
                 '\n    \U0001f551 ' + job[7] + \
                 '\n    💰 ' + job[3]
        bot.send_message(user_id, output)
    return 1


if __name__ == '__main__':
    bot.polling(none_stop=True)
    # bot.polling(none_stop=False)