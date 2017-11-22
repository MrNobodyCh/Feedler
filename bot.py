# -*- coding: utf-8 -*-
import sys
import time
import logging

import botan
import telebot

from telebot import types

from getters import RssFinder, RssParser, DBGetter, texts, GooGl
from config import BotSettings, ResourcesSettings, RssSettings, DBSettings, APISettings

reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig(filename='logs/debug.log', level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S %p")

bot = telebot.TeleBot(BotSettings.TOKEN)


@bot.message_handler(commands=["menu"])
def menu_command(message):
    main_menu_worker(message)
    botan.track(APISettings.BOTAN_TOKEN, message.chat.id, None, message.text)


@bot.message_handler(commands=["subscriptions"])
def subscriptions_command(message):
    subscriptions_menu(message)


@bot.message_handler(commands=["search"])
def search_command(message):
    enter_your_site_menu(message)


@bot.message_handler(commands=["top5"])
def top5_command(message):
    countries_menu(message)


@bot.message_handler(commands=["vk"])
def vk_command(message):
    vk_groups_menu(message)


@bot.message_handler(commands=["feedback"])
def feedback_command(message):
    feedback_menu(message)


@bot.message_handler(commands=["language"])
def language_command(message):
    change_language_menu(message)


@bot.message_handler(commands=["donate"])
def donate_command(message):
    donate(message)


@bot.message_handler(commands=["rate"])
def rate_command(message):
    rate(message)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts(message.chat.id).HELP)
def help_menu(message):
    user = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=texts(user).SUPPORT_TEAM, url=texts(user).SUPPORT_TEAM_LINK))
    markup.add(types.InlineKeyboardButton(text=texts(user).DONATE, url='http://www.donationalerts.ru/r/feedler'))
    bot.send_message(message.chat.id, text=texts(user).LIST_OF_COMMANDS, reply_markup=markup, parse_mode="Markdown")
    botan.track(APISettings.BOTAN_TOKEN, message.chat.id, None, message.text)


@bot.message_handler(commands=["start"])
def language_menu(message):
    user = message.chat.id
    user_lang = DBGetter(DBSettings.HOST).get("SELECT language FROM users_language "
                                              "WHERE user_id = %s" % message.chat.id)
    # potentially winbacker
    if len(user_lang) > 0:
        bot.send_message(message.chat.id, text=texts(user).WELCOME_BACK % message.chat.first_name)
        DBGetter(DBSettings.HOST).insert("UPDATE users_language SET active_status = TRUE")
        main_menu_worker(message)
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(u"\U0001F1F7\U0001F1FA Russian", callback_data="russian_new"),
                   types.InlineKeyboardButton(u"\U0001F1EC\U0001F1E7 English", callback_data="english_new"))
        bot.send_message(message.chat.id, text=u"Hi, %s! \u270b \nSelect your language:"
                                               % message.chat.first_name, reply_markup=markup)
        botan.track(APISettings.BOTAN_TOKEN, message.chat.id, None, "New User!")


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] in ["english", "russian"])
def main_menu(call):
    user = call.message.chat.id
    # set language
    if call.data.split('_')[0] == "russian" and call.data.split('_')[1] == "new":
        DBGetter(DBSettings.HOST).insert("INSERT INTO users_language (user_id, language) "
                                         "SELECT %s, '%s' WHERE NOT EXISTS "
                                         "(SELECT user_id FROM users_language WHERE user_id = %s)"
                                         % (call.message.chat.id, 'russian', call.message.chat.id))
    if call.data.split('_')[0] == "english" and call.data.split('_')[1] == "new":
        DBGetter(DBSettings.HOST).insert("INSERT INTO users_language (user_id, language) "
                                         "SELECT %s, '%s' WHERE NOT EXISTS "
                                         "(SELECT user_id FROM users_language WHERE user_id = %s)"
                                         % (call.message.chat.id, 'english', call.message.chat.id))
    # change language
    if call.data.split('_')[0] == "russian" and call.data.split('_')[1] == "change":
        DBGetter(DBSettings.HOST).insert("UPDATE users_language SET language = 'russian' "
                                         "WHERE user_id = %s" % call.message.chat.id)
        bot.send_message(call.message.chat.id, text=texts(user).CHANGED_LANGUAGE)
    if call.data.split('_')[0] == "english" and call.data.split('_')[1] == "change":
        DBGetter(DBSettings.HOST).insert("UPDATE users_language SET language = 'english' "
                                         "WHERE user_id = %s" % call.message.chat.id)
        bot.send_message(call.message.chat.id, text=texts(user).CHANGED_LANGUAGE)
    main_menu_worker(call.message)


@bot.callback_query_handler(func=lambda call: call.data == "supported")
def supported_user(call):
    user = call.message.chat.id
    DBGetter(DBSettings.HOST).insert("UPDATE users_language SET supported = TRUE "
                                     "WHERE user_id = %s" % call.message.chat.id)
    bot.send_message(call.message.chat.id, text=texts(user).GOT_IT)
    botan.track(APISettings.BOTAN_TOKEN, call.message.chat.id, None, call.data)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts(message.chat.id).DONATE)
def donate(message):
    user = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=texts(user).DONATE, url='http://www.donationalerts.ru/r/feedler'))
    bot.send_message(user, text=texts(user).IF_YOUR_LIKE, reply_markup=markup, parse_mode="Markdown")
    botan.track(APISettings.BOTAN_TOKEN, message.chat.id, None, message.text)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts(message.chat.id).RATE_BOT)
def rate(message):
    user = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=texts(user).RATE_BOT,
                                          url='https://telegram.me/storebot?start=Feedler_bot'))
    bot.send_message(user, text=texts(user).RATE_ME, reply_markup=markup)
    botan.track(APISettings.BOTAN_TOKEN, message.chat.id, None, message.text)


@bot.message_handler(content_types=['text'],
                     func=lambda message: message.text == texts(message.chat.id).CHANGE_LANGUAGE)
def change_language_menu(message):
    user = message.chat.id
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(u"\U0001F1F7\U0001F1FA Russian", callback_data="russian_change"),
               types.InlineKeyboardButton(u"\U0001F1EC\U0001F1E7 English", callback_data="english_change"))
    bot.send_message(message.chat.id, text=texts(user).SELECT_LANGUAGE, reply_markup=markup)


def main_menu_worker(message):
    user = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(texts(user).TOP_PORTALS, texts(user).ENTER_YOUR_SITE)
    markup.row(texts(user).VK, texts(user).SUBSCRIPTIONS)
    markup.row(texts(user).HELP, texts(user).RATE_BOT)
    bot.send_message(message.chat.id, text=texts(user).MAKE_YOUR_CHOICE, reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts(message.chat.id).TOP_PORTALS)
def countries_menu(message):
    user = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(texts(user).RUSSIA, texts(user).BELARUS)
    markup.row(texts(user).UKRAINE, texts(user).WORLD)
    markup.row(texts(user).BACK_TO_MAIN_MENU)
    bot.send_message(message.chat.id, text=texts(user).CHOOSE_THE_COUNTRY, reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts(message.chat.id).VK)
def vk_groups_menu(message):
    user = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(texts(user).TOP_PUBLICS)
    markup.row(texts(user).BACK_TO_MAIN_MENU)
    bot.send_message(message.chat.id, text=texts(user).MAKE_YOUR_CHOICE, reply_markup=markup)
    botan.track(APISettings.BOTAN_TOKEN, message.chat.id, None, message.text)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts(message.chat.id).FEEDBACK)
def feedback_menu(message):
    user = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(texts(user).BACK_TO_MAIN_MENU)
    msg = bot.send_message(message.chat.id, text=texts(user).ENTER_FEEDBACK, reply_markup=markup)
    bot.register_next_step_handler(msg, process_feedback)
    botan.track(APISettings.BOTAN_TOKEN, message.chat.id, None, message.text)


def process_feedback(message):
    user = message.chat.id
    feedback = (message.text[:2997] + '...') if len(message.text) > 2997 else message.text
    if feedback not in BotSettings.COMMANDS and feedback != texts(user).BACK_TO_MAIN_MENU:
        sql = "INSERT INTO users_feedback (user_id, feedback) VALUES (%s, %s)"
        DBGetter(DBSettings.HOST).insert(sql, (int(user), str(feedback)))
        bot.send_message(message.chat.id, text=texts(user).THANKS_FOR_FEEDBACK)
        main_menu_worker(message)


@bot.message_handler(content_types=['text'],
                     func=lambda message: message.text in [texts(message.chat.id).ENTER_YOUR_SITE,
                                                           texts(message.chat.id).ENTER_ANOTHER_SITE])
def enter_your_site_menu(message):
    user = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(texts(user).BACK_TO_MAIN_MENU)
    msg = bot.send_message(message.chat.id, text=texts(user).ENTER_SITE_OR_RSS, reply_markup=markup)
    bot.register_next_step_handler(msg, process_url)
    botan.track(APISettings.BOTAN_TOKEN, message.chat.id, None, message.text)


paginate_rss = {}
paginate_sub = {}
paginate_top_memes = {}
paginate_top_sites = {}


def chunkIt(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out


def process_url(message):
    user = message.chat.id
    url = message.text.lower()
    if url in ResourcesSettings.RESOURCES and url != texts(user).BACK_TO_MAIN_MENU.lower():
        bot.send_message(message.chat.id, text=texts(user).REQUESTED_SITE_PRESENTS)
        country = ResourcesSettings(url).get_country_by_resource()
        top_countries(country=country, action="send_message", handler_type=message)
    elif url in BotSettings.COMMANDS:
        pass
    elif url not in ResourcesSettings.RESOURCES and url != texts(user).BACK_TO_MAIN_MENU.lower():
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        bot.send_message(message.chat.id, text=texts(user).SEARCHING, reply_markup=keyboard)
        try:
            menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
            feeds = RssFinder(str(url.lower())).find_feeds()
            to_show = []
            if len(feeds) > 0:
                if len(feeds) < 5:
                    for feed in feeds:
                        menu.row(u"%s. \U0001F4E8 %s" % (str(feeds.index(feed) + 1), str(feed[1]))),
                        to_show.append("%s. %s - %s\n" % (str(feeds.index(feed) + 1), str(feed[0]), str(feed[1])))
                    menu.row(texts(user).ENTER_ANOTHER_SITE)
                    menu.row(texts(user).BACK_TO_MAIN_MENU)
                    bot.send_message(message.chat.id,
                                     text=texts(user).SELECT_RSS_CHANNEL % str(len(feeds)) + '\n' + ''.join(to_show) +
                                     '\n' + texts(user).YOU_CAN_SUBSCRIBE, reply_markup=menu)
                if len(feeds) > 5:
                    paginate_rss[user] = feeds
                    menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    markup = types.InlineKeyboardMarkup()
                    to_show = []
                    for feed in chunkIt(paginate_rss.get(user), float('%.1f' % len(paginate_rss.get(user))) / 5)[0]:
                        to_show.append("%s. %s - %s\n" % (str(paginate_rss.get(user).index(feed) + 1),
                                                          str(feed[0]), str(feed[1])))
                    for feed in paginate_rss.get(user):
                        menu.row(u"%s. \U0001F4E8 %s" % (str(paginate_rss.get(user).index(feed) + 1), str(feed[1]))),
                    row = [types.InlineKeyboardButton(u"\u27A1", callback_data=">>_%s_rss" % 1)]
                    markup.row(*row)
                    menu.row(texts(message.chat.id).ENTER_ANOTHER_SITE)
                    menu.row(texts(message.chat.id).BACK_TO_MAIN_MENU)
                    bot.send_message(message.chat.id,
                                     text=texts(message.chat.id).SELECT_RSS_CHANNEL % str(len(feeds)) + '\n' +
                                     ''.join(to_show), reply_markup=markup)
                    bot.send_message(message.chat.id, text=texts(message.chat.id).YOU_CAN_SUBSCRIBE, reply_markup=menu,
                                     parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, text=texts(user).RSS_FEEDS_NOT_FOUND)
                enter_your_site_menu(message)
        except Exception as error:
            logging.error(error)
            bot.send_message(message.chat.id, text=texts(user).REQUESTED_SITE_RETURN_ERROR % error,
                             parse_mode="Markdown")
    botan.track(APISettings.BOTAN_TOKEN, message.chat.id, None, "Поиск RSS: %s" % url)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] in [">>", "<<"])
def pagination_worker(call):
    user = call.message.chat.id
    # pagination for the found RSS feeds
    if call.data.split("_")[2] == "rss":
        to_show = []
        markup = types.InlineKeyboardMarkup()
        try:
            for feed in chunkIt(paginate_rss.get(user),
                                float('%.1f' % len(paginate_rss.get(user))) / 5)[int(call.data.split("_")[1])]:
                to_show.append("%s. %s - %s\n" % (str(paginate_rss.get(user).index(feed) + 1),
                                                  str(feed[0]), str(feed[1])))
            row = [types.InlineKeyboardButton(u"\u2B05", callback_data="<<_%s_rss"
                                                                       % (int(call.data.split("_")[1]) - 1)),
                   types.InlineKeyboardButton(u"\u27A1", callback_data=">>_%s_rss"
                                                                       % (int(call.data.split("_")[1]) + 1))]
            markup.row(*row)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=texts(call.message.chat.id).SELECT_RSS_CHANNEL
                                  % str(len(paginate_rss.get(user))) + '\n' + ''.join(to_show), reply_markup=markup)
        except (IndexError, TypeError):
            pass

    # pagination for user subscriptions
    if call.data.split("_")[2] == "sub":
        to_show = []
        markup = types.InlineKeyboardMarkup()
        try:
            for item in chunkIt(paginate_sub.get(user),
                                float('%.1f' % len(paginate_sub.get(user))) / 5)[int(call.data.split("_")[1])]:
                if item[1] is None:
                    heading = "%s. %s\n" % (str(paginate_sub.get(user).index(item) + 1), item[0])
                else:
                    heading = "%s. %s (%s)\n" % (str(paginate_sub.get(user).index(item) + 1), item[0], item[1])
                to_show.append(heading)
            row = [types.InlineKeyboardButton(u"\u2B05", callback_data="<<_%s_sub"
                                                                       % (int(call.data.split("_")[1]) - 1)),
                   types.InlineKeyboardButton(u"\u27A1", callback_data=">>_%s_sub"
                                                                       % (int(call.data.split("_")[1]) + 1))]
            markup.row(*row)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=texts(call.message.chat.id).LIST_OF_SUBSCRIPTIONS + '\n' + ''.join(to_show),
                                  reply_markup=markup)
        except (IndexError, TypeError):
            pass

    # pagination for top sites
    if call.data.split("_")[2] == "sites":
        markup = types.InlineKeyboardMarkup()
        try:
            for news in chunkIt(paginate_top_sites.get(user),
                                float('%.1f' % len(paginate_top_sites.get(user))) / 1)[int(call.data.split("_")[1])]:
                markup.add(types.InlineKeyboardButton(text=texts(user).READ_MORE, url=news[2]))
                row = [types.InlineKeyboardButton(u"\u2B05", callback_data="<<_%s_sites_%s_%s_%s"
                                                                           % (int(call.data.split("_")[1]) - 1,
                                                                              call.data.split("_")[3],
                                                                              call.data.split("_")[4],
                                                                              call.data.split("_")[5])),
                       types.InlineKeyboardButton(u"\u27A1", callback_data=">>_%s_sites_%s_%s_%s"
                                                                           % (int(call.data.split("_")[1]) + 1,
                                                                              call.data.split("_")[3],
                                                                              call.data.split("_")[4],
                                                                              call.data.split("_")[5]))]
                markup.row(*row)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text="%s\n%s" % (news[0], news[1]), reply_markup=markup)
        except (IndexError, TypeError):
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text=texts(user).CHOOSE_ANOTHER_SECTION,
                                                  callback_data="%s_%s" % (call.data.split("_")[3],
                                                                           call.data.split("_")[4])))
            bot.send_message(chat_id=call.message.chat.id,
                             text=texts(user).ALL_LASTEST_NEWS_DISPLAYED % call.data.split("_")[5],
                             disable_notification=True, reply_markup=markup, parse_mode="Markdown")

    # pagination for vk memes (pics, gifs)
    if call.data.split("_")[2] == "memes":
        markup = types.InlineKeyboardMarkup()
        row = [types.InlineKeyboardButton(u"\u2B05", callback_data="<<_%s_memes" % (int(call.data.split("_")[1]) - 1)),
               types.InlineKeyboardButton(u"\u27A1", callback_data=">>_%s_memes" % (int(call.data.split("_")[1]) + 1))]
        markup.row(*row)
        try:
            for x in chunkIt(paginate_top_memes.get(user),
                             float('%.1f' % len(paginate_top_memes.get(user))) / 1)[int(call.data.split("_")[1])]:
                # x[0] - caption, x[1] - type, x[2] - file_id
                # отправляем просто картинки
                if x[1] == "photo_no_caption":
                    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                    bot.send_photo(call.message.chat.id, photo=x[2], disable_notification=True, reply_markup=markup)

                # отправляем картинки с подписью
                if x[1] == "photo_with_caption":
                    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                    bot.send_photo(call.message.chat.id, photo=x[2], caption=x[0], disable_notification=True,
                                   reply_markup=markup)

                # отправляем просто гифки
                if x[1] == "gifs_no_caption":
                    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                    bot.send_document(call.message.chat.id, data=x[2], disable_notification=True, reply_markup=markup)

                # отправляем гифки с подписью
                if x[1] == "gifs_with_caption":
                    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                    bot.send_document(call.message.chat.id, data=x[2], caption=x[0], disable_notification=True,
                                      reply_markup=markup)
        except (IndexError, TypeError):
            bot.send_message(chat_id=call.message.chat.id, text=texts(user).ALL_LASTEST_POSTS_DISPLAYED,
                             disable_notification=True, parse_mode="Markdown")
            top_vk_groups(action="send_message", handler_type=call.message)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts(message.chat.id).SUBSCRIPTIONS)
def subscriptions_menu(message):
    user = message.chat.id
    subscriptions = DBGetter(DBSettings.HOST).get("SELECT subscription, description FROM "
                                                  "users_subscriptions WHERE user_id = %s" % user)
    if len(subscriptions) > 0:
        if len(subscriptions) < 5:
            menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
            to_show = []
            x = 0
            for item in subscriptions:
                x += 1
                if item[1] is None:
                    heading = "%s. %s\n" % (x, item[0])
                else:
                    heading = "%s. %s (%s)\n" % (x, item[0], item[1])
                to_show.append(heading)
                menu.row(u"%s. \u274C %s" % (x, item[0]))
            menu.row(texts(user).BACK_TO_MAIN_MENU)
            bot.send_message(message.chat.id,
                             text=texts(user).LIST_OF_SUBSCRIPTIONS + '\n' + ''.join(to_show) + '\n' + texts(
                                 user).YOU_CAN_UNSUBSCRIBE, reply_markup=menu)
        if len(subscriptions) > 5:
            paginate_sub[user] = subscriptions
            menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup = types.InlineKeyboardMarkup()
            to_show = []
            x = 0
            for item in chunkIt(paginate_sub.get(user), float('%.1f' % len(paginate_sub.get(user))) / 5)[0]:
                x += 1
                if item[1] is None:
                    heading = "%s. %s\n" % (x, item[0])
                else:
                    heading = "%s. %s (%s)\n" % (x, item[0], item[1])
                to_show.append(heading)
            x = 0
            for item in paginate_sub.get(user):
                x += 1
                menu.row(u"%s. \u274C %s" % (x, item[0])),
            row = [types.InlineKeyboardButton(u"\u27A1", callback_data=">>_%s_sub" % 1)]
            markup.row(*row)
            menu.row(texts(message.chat.id).BACK_TO_MAIN_MENU)
            bot.send_message(message.chat.id, text=texts(user).LIST_OF_SUBSCRIPTIONS + '\n' + ''.join(to_show),
                             reply_markup=markup)
            bot.send_message(message.chat.id, text=texts(user).YOU_CAN_UNSUBSCRIBE,
                             reply_markup=menu, parse_mode="Markdown")
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        bot.send_message(message.chat.id, text=texts(user).YOU_HAVE_NO_SUBSCRIPTIONS, reply_markup=keyboard)
    botan.track(APISettings.BOTAN_TOKEN, message.chat.id, None, message.text)


@bot.message_handler(content_types=['text'],
                     func=lambda message: len(set(message.text.split()) & {u"\U0001F4E8", u"\u274C"}) == 1 or len(
                         set(message.text.split()) & set(texts(message.chat.id).SUBSCRIBE_TO.split())) == 3 or len(
                         set(message.text.split()) & set(texts(message.chat.id).UNSUBSCRIBE_FROM.split())) == 3)
def subscribe_unsubscribe_user(message):
    user = message.chat.id
    # subscribe/unsubscribe to unknown resources
    if message.text.split()[1] == u"\U0001F4E8":
        resource_name = message.text.split()[2]
        check_subscribe = DBGetter(DBSettings.HOST).get("SELECT count(*) FROM users_subscriptions "
                                                        "WHERE user_id = '%s' AND subscription = '%s'"
                                                        % (int(user), resource_name))[0][0]
        if check_subscribe > 0:
            bot.send_message(message.chat.id, text=texts(user).ALREADY_SUBSCRIBED_TO % resource_name)
        else:
            try:
                description = RssFinder(resource_name).find_feeds()[0][0]
            except Exception:
                description = None
            try:
                latest_date = DBGetter(DBSettings.HOST).get("SELECT publish_date FROM news_portals "
                                                            "WHERE portal_name = '%s' ORDER BY publish_date DESC"
                                                            % '%s' % resource_name)[:1][0][0]
            except Exception:
                latest_date = int(time.time())
            # add resource for current user
            sql = "INSERT INTO users_subscriptions (user_id, subscription, " \
                  "description, latest_date) VALUES (%s, %s, %s, %s)"
            DBGetter(DBSettings.HOST).insert(sql, (user, resource_name, description, latest_date))
            bot.send_message(message.chat.id, text=texts(user).SUCCESSFULLY_SUBSCRIBED % resource_name)
            # send latest news from rss feed
            latest_news_from_db = DBGetter(DBSettings.HOST).get("SELECT news_headline, news_short_url, news_full_url "
                                                                "FROM news_portals WHERE rss_url = '%s' "
                                                                "ORDER BY publish_date DESC" % resource_name)[:1]
            if description is None:
                heading = resource_name
            else:
                heading = "%s (%s)" % (resource_name, description)
            if latest_news_from_db > 0:
                for news in latest_news_from_db:
                    markup = types.InlineKeyboardMarkup()
                    markup.add(types.InlineKeyboardButton(text=texts(user).READ_MORE, url=news[2]))
                    bot.send_message(chat_id=user,
                                     text=texts(user).HERE_IS_LATEST_NEWS % heading + '\n\n' + "%s\n%s"
                                                                                               % (news[0], news[1]),
                                     disable_notification=True, reply_markup=markup)
            if len(latest_news_from_db) == 0:
                try:
                    latest_news_from_http = RssParser(str(resource_name)).get_news_for_known_resource()[:1]
                    for news in latest_news_from_http:
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton(text=texts(user).READ_MORE, url=news[1]))
                        bot.send_message(chat_id=user, text=texts(user).HERE_IS_LATEST_NEWS % heading + '\n\n' +
                                         "%s\n%s" % (news[0], GooGl().short_link(news[1])),
                                         disable_notification=True, reply_markup=markup)
                except Exception as error:
                    logging.error(error)
                    pass

    if message.text.split()[1] == u"\u274C":
        resource_name = message.text.split()[2]
        DBGetter(DBSettings.HOST).insert("DELETE FROM users_subscriptions WHERE user_id = %s "
                                         "AND subscription = '%s'" % (user, resource_name))
        bot.send_message(message.chat.id, text=texts(user).SUCCESSFULLY_UNSUBSCRIBED % resource_name)

    # subscribe/unsubscribe to top resources
    if message.text.split()[0] == u"\U0001F4E8":
        resource_name = message.text.split()[3]
        check_subscribe = DBGetter(DBSettings.HOST).get("SELECT count(*) FROM users_subscriptions "
                                                        "WHERE user_id = '%s' AND subscription = '%s'"
                                                        % (int(user), resource_name))[0][0]
        if check_subscribe > 0:
            bot.send_message(message.chat.id, text=texts(user).ALREADY_SUBSCRIBED_TO % resource_name)
        else:
            try:
                latest_date = DBGetter(DBSettings.HOST).get("SELECT publish_date FROM news_portals "
                                                            "WHERE portal_name = '%s' ORDER BY publish_date DESC"
                                                            % '%s' % resource_name)[:1][0][0]
            except Exception:
                latest_date = int(time.time())
            DBGetter(DBSettings.HOST).insert("INSERT INTO users_subscriptions (user_id, subscription, latest_date) "
                                             "VALUES (%s, '%s', %s)" % (user, resource_name, latest_date))
            bot.send_message(message.chat.id, text=texts(user).SUCCESSFULLY_SUBSCRIBED % resource_name)
    if message.text.split()[0] == u"\u274C":
        resource_name = message.text.split()[3]
        DBGetter(DBSettings.HOST).insert("DELETE FROM users_subscriptions WHERE user_id = %s "
                                         "AND subscription = '%s'" % (user, resource_name))
        bot.send_message(message.chat.id, text=texts(user).SUCCESSFULLY_UNSUBSCRIBED % resource_name)

    botan.track(APISettings.BOTAN_TOKEN, message.chat.id, None, message.text)


@bot.message_handler(content_types=['text'],
                     func=lambda message: message.text == texts(message.chat.id).BACK_TO_MAIN_MENU)
def back_main_menu(message):
    main_menu_worker(message)


@bot.message_handler(content_types=['text'],
                     func=lambda message: message.text == texts(message.chat.id).BACK_TO_COUNTRIES)
def back_to_countries(message):
    countries_menu(message)


def top_countries(country, action, handler_type):
    markup = types.InlineKeyboardMarkup()
    if country == "russia":
        markup.row(types.InlineKeyboardButton("Новости@Mail.Ru", callback_data="news.mail.ru_russia"))
        markup.row(types.InlineKeyboardButton("Яндекс.Новости", callback_data="news.yandex.ru_russia"))
        markup.row(types.InlineKeyboardButton("Рамблер/Новости", callback_data="rambler.ru_russia"))
        markup.row(types.InlineKeyboardButton("РБК", callback_data="rbc.ru_russia"))
        markup.row(types.InlineKeyboardButton("Lenta.ru", callback_data="lenta.ru_russia"))
    if country == "belarus":
        markup.row(types.InlineKeyboardButton("Onliner.by", callback_data="onliner.by_belarus"))
        markup.row(types.InlineKeyboardButton("Белорусский портал TUT.BY", callback_data="tut.by_belarus"))
        markup.row(types.InlineKeyboardButton("Хартия'97", callback_data="charter97.org_belarus"))
        markup.row(types.InlineKeyboardButton("UDF.BY", callback_data="udf.by_belarus"))
        markup.row(types.InlineKeyboardButton("БелТА", callback_data="belta.by_belarus"))
    if country == "ukraine":
        markup.row(types.InlineKeyboardButton("КорреспонденT.net", callback_data="korrespondent.net_ukraine"))
        markup.row(types.InlineKeyboardButton("Обозреватель.ua", callback_data="obozrevatel.com_ukraine"))
        markup.row(types.InlineKeyboardButton("ЦЕНЗОР.НЕТ", callback_data="censor.net.ua_ukraine"))
        markup.row(types.InlineKeyboardButton("ТЕЛЕГРАФ", callback_data="telegraf.com.ua_ukraine"))
        markup.row(types.InlineKeyboardButton("СЕГОДНЯ", callback_data="segodnya.ua_ukraine"))
    if country == "world":
        markup.row(types.InlineKeyboardButton("CNN", callback_data="edition.cnn.com_world"))
        markup.row(types.InlineKeyboardButton("The New York Times", callback_data="nytimes.com_world"))
        markup.row(types.InlineKeyboardButton("The Guardian", callback_data="theguardian.com_world"))
        markup.row(types.InlineKeyboardButton("The Washington Post", callback_data="washingtonpost.com_world"))
        markup.row(types.InlineKeyboardButton("BBC", callback_data="bbc.com_world"))
    if action == "send_message":
        bot.send_message(handler_type.chat.id, text=texts(handler_type.chat.id).SELECT_SITE, reply_markup=markup)
    elif action == "edit_message":
        bot.edit_message_text(chat_id=handler_type.message.chat.id, message_id=handler_type.message.message_id,
                              text=texts(handler_type.message.chat.id).SELECT_SITE, reply_markup=markup)
    botan.track(APISettings.BOTAN_TOKEN, None, country)


def top_vk_groups(action, handler_type):
    markup = types.InlineKeyboardMarkup()
    for name, group_id in ResourcesSettings.VK_GROUPS_IDS.iteritems():
        markup.row(types.InlineKeyboardButton("%s" % name, callback_data="%s" % group_id))
    if action == "send_message":
        bot.send_message(handler_type.chat.id, text=texts(handler_type.chat.id).SELECT_PUBLIC, reply_markup=markup)
    elif action == "edit_message":
        bot.edit_message_text(chat_id=handler_type.message.chat.id, message_id=handler_type.message.message_id,
                              text=texts(handler_type.message.chat.id).SELECT_PUBLIC, reply_markup=markup)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts(message.chat.id).TOP_PUBLICS)
def vk_top(message):
    top_vk_groups(action="send_message", handler_type=message)
    botan.track(APISettings.BOTAN_TOKEN, message.chat.id, None, message.text)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts(message.chat.id).RUSSIA)
def russia_top(message):
    top_countries(country="russia", action="send_message", handler_type=message)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts(message.chat.id).BELARUS)
def belarus_top(message):
    top_countries(country="belarus", action="send_message", handler_type=message)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts(message.chat.id).UKRAINE)
def ukraine_top(message):
    top_countries(country="ukraine", action="send_message", handler_type=message)


@bot.message_handler(content_types=['text'], func=lambda message: message.text == texts(message.chat.id).WORLD)
def world_top(message):
    top_countries(country="world", action="send_message", handler_type=message)


@bot.callback_query_handler(func=lambda call: call.data in ResourcesSettings.TOP_COUNTRIES)
def back_to_top_sites(call):
    top_countries(country=call.data, action="edit_message", handler_type=call)


@bot.callback_query_handler(func=lambda call: call.data in ResourcesSettings.VK_GROUPS_IDS.keys())
def back_to_top_vk_groups(call):
    top_vk_groups(action="edit_message", handler_type=call)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] in ResourcesSettings.RESOURCES)
def top_site_menu(call):
    user = call.message.chat.id
    markup = types.InlineKeyboardMarkup()
    for k, v in ResourcesSettings(call.data.split('_')[0]).get_categories().iteritems():
        markup.row(types.InlineKeyboardButton(k.split('_')[0],
                                              callback_data="http://%s_%s" % (call.data.split('_')[0], v)))
    markup.row(types.InlineKeyboardButton(texts(user).BACK_TO_SITE_SELECTION, callback_data=call.data.split('_')[1]))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=texts(user).CHOOSE_SECTION % call.data.split('_')[0], reply_markup=markup)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    is_subscribe = DBGetter(DBSettings.HOST).get("SELECT count(*) FROM users_subscriptions "
                                                 "WHERE subscription = '%s' AND user_id = %s" %
                                                 (call.data.split('_')[0], user))[0][0]
    if is_subscribe == 0:
        keyboard.row(texts(user).SUBSCRIBE_TO % call.data.split('_')[0])
    if is_subscribe == 1:
        keyboard.row(texts(user).UNSUBSCRIBE_FROM % call.data.split('_')[0])
    keyboard.row(texts(user).BACK_TO_COUNTRIES)
    if is_subscribe == 0:
        bot.send_message(chat_id=call.message.chat.id,
                         text=texts(user).YOU_CAN_SUBSCRIBE_TO % call.data.split('_')[0],
                         reply_markup=keyboard)
    if is_subscribe == 1:
        bot.send_message(chat_id=call.message.chat.id,
                         text=texts(user).YOU_CAN_UNSUBSCRIBE_FROM % call.data.split('_')[0],
                         reply_markup=keyboard)
    botan.track(APISettings.BOTAN_TOKEN, call.message.chat.id, None, call.data)


@bot.callback_query_handler(func=lambda call: call.data.split('_')[0] in RssSettings.RESOURCES_DOMAINS)
def get_news_by_top_resources(call):
    user = call.message.chat.id
    resource = call.data.split('_')[0].replace("http://", "")
    domain = call.data.split('_')[0]
    category_rss = call.data.split('_', 1)[1]
    category_name = str
    country = ResourcesSettings(resource).get_country_by_resource()
    rss_url = RssSettings(domain).get_full_rss_url() % category_rss
    for k, v in ResourcesSettings(resource).get_categories().iteritems():
        if v == category_rss:
            category_name = k.split('_')[0]
            bot.send_message(call.message.chat.id,
                             text=texts(user).LATEST_NEWS % (resource, category_name), parse_mode="Markdown")
    latest_news = DBGetter(DBSettings.HOST).get("SELECT news_headline, news_short_url, news_full_url "
                                                "FROM news_portals WHERE rss_url = '%s' "
                                                "ORDER BY publish_date DESC" % rss_url)
    paginate_top_sites[user] = latest_news
    for news in chunkIt(paginate_top_sites.get(user), float('%.1f' % len(paginate_top_sites.get(user))) / 1)[0]:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text=texts(user).READ_MORE, url=news[2]))
        row = [types.InlineKeyboardButton(u"\u27A1", callback_data=">>_%s_sites_%s_%s_%s" % (1, resource, country,
                                                                                             category_name))]
        markup.row(*row)
        bot.send_message(chat_id=call.message.chat.id, text="%s\n%s" % (news[0], news[1]),
                         disable_notification=True, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in str(ResourcesSettings.VK_GROUPS_IDS.values()))
def get_memes_by_top_vk_groups(call):
    user = call.message.chat.id
    vk_group_id = int(call.data)
    for k, v in ResourcesSettings.VK_GROUPS_IDS.iteritems():
        if v == vk_group_id:
            vk_group_name = k
            bot.send_message(chat_id=call.message.chat.id,
                             text=texts(user).RECENT_PUBLIC_POSTS % vk_group_name, parse_mode="Markdown")
    vk_feed = DBGetter(DBSettings.HOST).get("SELECT caption, type, file_id FROM vk_groups_posts WHERE file_id "
                                            "IS NOT NULL AND group_id = %s ORDER BY post_date DESC" % vk_group_id)
    paginate_top_memes[user] = vk_feed
    markup = types.InlineKeyboardMarkup()
    row = [types.InlineKeyboardButton(u"\u27A1", callback_data=">>_%s_memes" % 1)]
    markup.row(*row)
    for x in chunkIt(paginate_top_memes.get(user), float('%.1f' % len(paginate_top_memes.get(user))) / 1)[0]:
        # x[0] - caption, x[1] - type, x[2] - file_id
        # отправляем просто картинки
        if x[1] == "photo_no_caption":
            bot.send_photo(call.message.chat.id, photo=x[2], disable_notification=True, reply_markup=markup)

        # отправляем картинки с подписью
        if x[1] == "photo_with_caption":
            bot.send_photo(call.message.chat.id, photo=x[2], caption=x[0],
                           disable_notification=True, reply_markup=markup)

        # отправляем просто гифки
        if x[1] == "gifs_no_caption":
            bot.send_document(call.message.chat.id, data=x[2], disable_notification=True, reply_markup=markup)

        # отправляем гифки с подписью
        if x[1] == "gifs_with_caption":
            bot.send_document(call.message.chat.id, data=x[2], caption=x[0],
                              disable_notification=True, reply_markup=markup)
    botan.track(APISettings.BOTAN_TOKEN, call.message.chat.id, None, call.data)

while True:

    try:

        bot.polling(none_stop=True)

    # ConnectionError and ReadTimeout because of possible timeout of the requests library

    # TypeError for moviepy errors

    # maybe there are others, therefore Exception

    except Exception as e:
        logging.error(e)
        time.sleep(5)
