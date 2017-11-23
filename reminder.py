# -*- coding: utf-8 -*-
import sys
import logging
import requests

import telebot

from telebot import types

from getters import DBGetter, texts
from config import DBSettings, BotSettings

reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig(filename='logs/reminder.log', level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S %p")
logging.getLogger("requests").setLevel(logging.WARNING)


def reminder():
    if requests.get("http://storebot.me").status_code == 200:
        async_bot = telebot.AsyncTeleBot(BotSettings.TOKEN)
        users = DBGetter(DBSettings.HOST).get("SELECT user_id FROM users_language WHERE "
                                              "supported = FALSE AND active_status = TRUE")
        for user in users:
            user_id = user[0]
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text=texts(user_id).RATE_BOT,
                                                  url='https://telegram.me/storebot?start=Feedler_bot'))
            markup.add(types.InlineKeyboardButton(texts(user_id).ALREADY_SUPPORTED, callback_data="supported"))
            msg = async_bot.send_message(user_id, text=texts(user_id).REMINDER,
                                         reply_markup=markup, parse_mode="Markdown")
            result = msg.wait()
            # check that the user is still active
            try:
                logging.info("Send reminder for user: %s" % result.chat.id)
            except Exception as e:
                logging.info("%s. No active user with user_id: %s and Response Status: %s" % (e, user_id, result))
                DBGetter(DBSettings.HOST).insert("UPDATE users_language SET active_status = FALSE "
                                                 "WHERE user_id = '%s'" % int(user_id))
    else:
        logging.info("Storebot.me is currently unavailable")


reminder()
