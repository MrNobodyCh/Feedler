# -*- coding: utf-8 -*-
import logging
import sys

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
        users = DBGetter(DBSettings.HOST).get("SELECT DISTINCT ON (user_id) * FROM users_subscriptions")
        for user in users:
            not_supported = DBGetter(DBSettings.HOST).get("SELECT user_id FROM users_language "
                                                          "WHERE user_id = '%s' AND supported = FALSE" % user[0])
            for x in not_supported:
                user_id = x[0]
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton(text=texts(user_id).RATE_BOT,
                                                      url='https://telegram.me/storebot?start=Feedler_bot'))
                markup.add(types.InlineKeyboardButton(texts(user_id).ALREADY_SUPPORTED, callback_data="supported"))
                async_bot.send_message(user_id, text=texts(user_id).REMINDER, reply_markup=markup, parse_mode="Markdown")
                logging.info("Send reminder for user: %s" % user_id)
    else:
        logging.info("Storebot.me is currently unavailable")


reminder()
