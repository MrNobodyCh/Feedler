# -*- coding: utf-8 -*-
import sys
import logging

import requests
import telebot

from telebot import types

from getters import DBGetter, RssParser, GooGl, texts
from config import ResourcesSettings, DBSettings, RssSettings, BotSettings

reload(sys)
sys.setdefaultencoding('utf-8')

logging.basicConfig(filename='logs/news_grabber.log', level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S %p")
logging.getLogger("requests").setLevel(logging.WARNING)

async_bot = telebot.AsyncTeleBot(BotSettings.TOKEN)


class NewsGrabber(object):
    def __init__(self, url):
        self.rss_url = url

    def get_news(self, portal_name):
        logging.info("==================Starting grabber for %s==================" % self.rss_url)
        for news in RssParser(self.rss_url).get_news_for_known_resource():
            check_exists = DBGetter(DBSettings.HOST).get("SELECT COUNT(*) FROM news_portals "
                                                         "WHERE portal_name = '%s' AND news_full_url = '%s' "
                                                         "AND rss_url = '%s'"
                                                         % (portal_name, news[1], self.rss_url))[0][0]
            if check_exists == 0:
                sql = "INSERT INTO news_portals (portal_name, rss_url, news_headline, news_short_url, " \
                      "news_full_url, publish_date) VALUES (%s, %s, %s, %s, %s, %s) "
                # news[0].replace("&nbsp;", " ") -- onliner иногда добавляет &nbsp; в конец заголовка
                DBGetter(DBSettings.HOST).insert(sql, (portal_name, self.rss_url, news[0].replace("&nbsp;", " "),
                                                       GooGl().short_link(news[1]), news[1], int(news[2])))
                logging.info("Inserting new post with url: %s" % news[1])
            if check_exists > 0:
                pass
        # удаляем из БД посты (по каждому RSS фиду кол-во не должно быть > 10)
        posts_count = DBGetter(DBSettings.HOST).get("SELECT COUNT(*) FROM news_portals "
                                                    "WHERE portal_name = '%s' "
                                                    "AND rss_url = '%s'" % (portal_name, self.rss_url))
        if int(posts_count[0][0]) > 10:
            to_delete = int(posts_count[0][0]) - 10
            delete_old_posts = "DELETE FROM news_portals WHERE ctid IN (SELECT ctid FROM news_portals " \
                               "WHERE rss_url = '%s' ORDER BY publish_date LIMIT %s)" % (self.rss_url, to_delete)
            DBGetter(DBSettings.HOST).insert(delete_old_posts)
            logging.info("Deleted %s news for RSS: %s" % (to_delete, self.rss_url))


def get_news_by_subscriptions(user):
    users = user
    for x in users:
        user_id = x[0]
        to_send = {}
        descriptions = {}
        subscriptions = DBGetter(DBSettings.HOST).get("SELECT subscription, description, latest_date "
                                                      "FROM users_subscriptions WHERE user_id = %s" % user_id)
        for sub in subscriptions:
            subscription = sub[0]
            description = sub[1]
            latest_date = sub[2]
            # берем свежие новости (не больше 10 по каждому ресурсу)
            latest_news = DBGetter(DBSettings.HOST).get("SELECT DISTINCT ON (news_headline) news_headline, "
                                                        "news_short_url, news_full_url, publish_date FROM news_portals "
                                                        "WHERE portal_name = '%s' AND publish_date > %s "
                                                        "ORDER BY news_headline, news_short_url, news_full_url, "
                                                        "publish_date" % (subscription, int(latest_date)))

            if len(latest_news) > 0:
                sorted_news = sorted(latest_news, key=lambda i: i[3], reverse=True)[:10]
                to_send.update({subscription: sorted_news})
                descriptions.update({subscription: description})
        total_numbering = 0
        news_count = 0
        for count in to_send.values():
            for _ in count:
                news_count += 1
        for key, value in to_send.iteritems():
            to_show = []
            numbering = 0
            for news in value:
                numbering += 1
                total_numbering += 1
                if total_numbering != news_count:
                    to_show.append("\n%s. %s - %s" % (numbering, news[0], news[1]))
                if total_numbering == news_count:
                    to_show.append(u"\n%s. %s - %s\n\n%s" % (numbering, news[0], news[1],
                                                             texts(user_id).ALL_FEEDS_UPDATED))
            if descriptions.get(key) is None:
                heading = key
            else:
                heading = "%s (%s)" % (key, descriptions.get(key))
            msg = async_bot.send_message(user_id, disable_web_page_preview=True,
                                         text=texts(user_id).HERE_IS_LATEST_NEWS % heading + '\n' + ''.join(to_show))
            result = msg.wait()
            # check that the user is still active
            try:
                logging.info("Send %s new posts for user %s and %s" % (len(value), result.chat.id, key))
                upd_latest_date = DBGetter(DBSettings.HOST).get("SELECT publish_date FROM news_portals WHERE "
                                                                "portal_name = '%s' ORDER BY publish_date "
                                                                "DESC LIMIT 1" % key)[0][0]
                DBGetter(DBSettings.HOST).insert("UPDATE users_subscriptions SET latest_date = '%s' "
                                                 "WHERE subscription = '%s' AND user_id = %s" %
                                                 (int(upd_latest_date), key, user_id))
            except Exception as err:
                logging.info("%s. No active user with user_id: %s and Response Status: %s" % (err, user_id, result))
                DBGetter(DBSettings.HOST).insert("UPDATE users_language SET active_status = FALSE "
                                                 "WHERE user_id = '%s'" % int(user_id))


def send_latest_news_to_channel():
    channel_news = DBGetter(DBSettings.HOST).get("SELECT DISTINCT ON (news_short_url) * FROM news_portals "
                                                 "WHERE portal_name in (%s) AND send_to_channel = FALSE "
                                                 "ORDER BY news_short_url, publish_date DESC;"
                                                 % str(ResourcesSettings.RESOURCES)[1:-1])
    logging.info("Starting send %s items to the channel" % len(channel_news))
    for news in channel_news:
        if ResourcesSettings(news[0]).get_country_by_resource() == "belarus":
            message_text = u"\U0001F1E7\U0001F1FE #%s\n%s\n%s"
        elif ResourcesSettings(news[0]).get_country_by_resource() == "russia":
            message_text = u"\U0001F1F7\U0001F1FA #%s\n%s\n%s"
        elif ResourcesSettings(news[0]).get_country_by_resource() == "ukraine":
            message_text = u"\U0001F1FA\U0001F1E6 #%s\n%s\n%s"
        elif ResourcesSettings(news[0]).get_country_by_resource() == "world":
            message_text = u"\U0001F30E #%s\n%s\n%s"
        else:
            message_text = "#%s\n%s\n%s"
        # send news to the channel
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text=u"\U0001F4F0 Read More", url=news[4]))
        msg = async_bot.send_message(chat_id="@the_latestnews",
                                     text=message_text % (news[0].replace(".", "_"), news[2], news[3]),
                                     disable_notification=True, reply_markup=markup)
        msg.wait()
        # mark send_to_channel == true
        DBGetter(DBSettings.HOST).insert("UPDATE news_portals SET send_to_channel = TRUE "
                                         "WHERE news_short_url = '%s'" % news[3])
    logging.info("Sending to the channel successfully finished. Was sent %s items" % len(channel_news))
    # send reminder about Feedler Bot into the channel
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=u"\U0001F916 Feedler Bot", url='https://t.me/Feedler_bot'))
    reminder = async_bot.send_message(chat_id="@the_latestnews",
                                      text=u"\U0001F1F7\U0001F1FA Все новости постятся в канал ботом "
                                           u"по имени *Feedler*. Он умеет еще много чего, советуем"
                                           u" попробовать!\n"
                                           u"\U0001F1EC\U0001F1E7 All news are posted to the "
                                           u"channel by a bot named *Feedler*. He knows a lot more, "
                                           u"we advise you to try it!", reply_markup=markup, parse_mode="Markdown")
    reminder.wait()


# update resources for which there are subscriptions
resources = DBGetter(DBSettings.HOST).get("SELECT * FROM (SELECT DISTINCT users_subscriptions.subscription "
                                          "FROM users_subscriptions, users_language "
                                          "WHERE users_language.user_id = users_subscriptions.user_id "
                                          "AND users_language.active_status = TRUE "
                                          "ORDER BY users_subscriptions.subscription) AS tmp")
for resource in resources:
    if resource[0] in ResourcesSettings.RESOURCES:
        for k, v in ResourcesSettings(resource[0]).get_categories().iteritems():
            resource_url = RssSettings("http://" + resource[0]).get_full_rss_url() % v
            try:
                requests.get(resource_url, timeout=10)
                NewsGrabber(resource_url).get_news(resource[0])
            except requests.exceptions.Timeout as e:
                logging.info("%s during processing the resource %s" % (e, resource_url))
                pass
            except (requests.exceptions.RequestException, Exception) as e:
                logging.info("%s during processing the resource %s" % (e, resource_url))
                pass
    else:
        try:
            requests.get(resource[0], timeout=10)
            NewsGrabber(resource[0]).get_news(resource[0])
        except requests.exceptions.Timeout as e:
            logging.info("%s during processing the resource %s" % (e, resource[0]))
            pass
        except (requests.exceptions.RequestException, Exception) as e:
            logging.info("%s during processing the resource %s" % (e, resource[0]))
            pass

# send the latest news to subscribers with active_status = true
send_to_users = DBGetter(DBSettings.HOST).get("SELECT * FROM (SELECT DISTINCT users_subscriptions.user_id FROM "
                                              "users_subscriptions, users_language WHERE "
                                              "users_language.user_id = users_subscriptions.user_id AND "
                                              "users_language.active_status = TRUE) AS tmp")
get_news_by_subscriptions(send_to_users)

# update resources from the top-5 section
for resource in ResourcesSettings.RESOURCES:
    if len([item for item in resources if item[0] == resource]) > 0:
        pass
    else:
        for a, b in ResourcesSettings(resource).get_categories().iteritems():
            resource_url = (RssSettings("http://" + resource).get_full_rss_url() % b)
            try:
                requests.get(resource_url, timeout=10)
                NewsGrabber(resource_url).get_news(resource)
            except requests.exceptions.Timeout as e:
                logging.info("%s during processing the resource %s" % (e, resource_url))
                pass
            except (requests.exceptions.RequestException, Exception) as e:
                logging.info("%s during processing the resource %s" % (e, resource_url))
                pass

send_latest_news_to_channel()
