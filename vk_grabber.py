# -*- coding: utf-8 -*-
import re
import sys
import urllib

import telebot
import vk_api
import logging

from getters import DBGetter
from config import APISettings, BotSettings, DBSettings

reload(sys)
sys.setdefaultencoding('utf8')

logging.basicConfig(filename='logs/vk_grabber.log', level=logging.INFO,
                    format="%(asctime)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S %p")
logging.getLogger("urllib").setLevel(logging.WARNING)


class VKGrabber(object):
    def __init__(self, url):
        self.api_url = url
        self.vk_session = self.api_url

    def get_vk_groups_news_feed(self, vk_group_id):

        try:
            self.vk_session.auth()
        except vk_api.AuthError as error_msg:
            print(error_msg)
            return

        tools = vk_api.VkTools(self.vk_session)

        wall = tools.get_all('wall.get', max_count=1, limit=1, values={'owner_id': -vk_group_id})
        logging.info("=================Starting grabber for group %s=================" % vk_group_id)
        vk_group_name = str(DBGetter(DBSettings.HOST).get("SELECT group_name FROM vk_groups_names "
                                                          "WHERE group_id = %s" % vk_group_id)[0][0])
        for item in wall["items"]:
            try:
                # игнорируем закрепленные посты
                if item["is_pinned"]:
                    continue
            except KeyError:
                pass
            try:
                try:
                    # игрорируем посты с несколькими картинками
                    if item["copy_history"]:
                        continue
                except KeyError:
                    pass

                # просто картинки
                if item["attachments"][0]["type"] == "photo" and item["text"] == "" \
                        and len(item["attachments"]) == 1 and int(item["marked_as_ads"]) == 0:
                    for x in item["attachments"][0]["photo"]:
                        try:
                            photo_size = re.search(r'\d+', x).group()
                        except AttributeError:
                            pass
                    query = "SELECT FROM vk_groups_posts WHERE doc_url = '%s'" % \
                            item["attachments"][0]["photo"]["photo_%s" % photo_size]
                    if len(DBGetter(DBSettings.HOST).get(query)) == 0:
                        # вставляем новый
                        DBGetter(DBSettings.HOST).insert("INSERT INTO vk_groups_posts (group_id, group_name, "
                                                         "doc_url, type, post_date) "
                                                         "VALUES (%s, '%s', '%s', 'photo_no_caption', %s)" %
                                                         (vk_group_id, vk_group_name,
                                                          item["attachments"][0]["photo"]["photo_%s" % photo_size],
                                                          item["date"]))
                        logging.info("Added new 'photo_no_caption' post with doc_url: %s" %
                                     item["attachments"][0]["photo"]["photo_%s" % photo_size])
                    else:
                        pass

                # картинки с подписью
                if item["attachments"][0]["type"] == "photo" and item["text"] != "" and "club" not in item["text"] \
                        and len(item["attachments"]) == 1 and int(item["marked_as_ads"]) == 0:
                    for x in item["attachments"][0]["photo"]:
                        try:
                            photo_size = re.search(r'\d+', x).group()
                        except AttributeError:
                            pass
                    query = "SELECT FROM vk_groups_posts WHERE doc_url = '%s'" % \
                            item["attachments"][0]["photo"]["photo_%s" % photo_size]
                    if len(DBGetter(DBSettings.HOST).get(query)) == 0:
                        # вставляем новый
                        DBGetter(DBSettings.HOST).insert(
                            "INSERT INTO vk_groups_posts (group_id, group_name, doc_url, type, caption, post_date)"
                            "VALUES (%s, '%s', '%s', 'photo_with_caption', '%s', %s)" %
                            (vk_group_id, vk_group_name, item["attachments"][0]["photo"]["photo_%s" % photo_size],
                             item["text"], item["date"]))
                        logging.info("Added new 'photo_with_caption' post with caption: %s and doc_url: %s" %
                                     (item["text"], item["attachments"][0]["photo"]["photo_%s" % photo_size]))
                    else:
                        pass

                # гифки без подписи
                if item["attachments"][0]["type"] == "doc" and item["text"] == "" \
                        and len(item["attachments"]) == 1 and int(item["marked_as_ads"]) == 0:
                    query = "SELECT FROM vk_groups_posts WHERE type = '%s' AND post_date = '%s'" % \
                            ('gifs_no_caption', item["date"])
                    if len(DBGetter(DBSettings.HOST).get(query)) == 0:
                        # вставляем новый
                        DBGetter(DBSettings.HOST).insert("INSERT INTO vk_groups_posts (group_id, group_name, "
                                                         "doc_url, type, post_date) "
                                                         "VALUES (%s, '%s', '%s', 'gifs_no_caption', %s)" %
                                                         (vk_group_id, vk_group_name,
                                                          item["attachments"][0]["doc"]["preview"]["video"]["src"],
                                                          item["date"]))
                        logging.info("Added new 'gifs_no_caption' post with doc_url: %s" %
                                     item["attachments"][0]["doc"]["preview"]["video"]["src"])
                    else:
                        pass

                # гифки с подписью
                if item["attachments"][0]["type"] == "doc" and item["text"] != "" and "club" not in item["text"] \
                        and len(item["attachments"]) == 1 and int(item["marked_as_ads"]) == 0:
                    query = "SELECT FROM vk_groups_posts WHERE type = '%s' AND caption = '%s'" % \
                            ('gifs_with_caption', item["text"])
                    if len(DBGetter(DBSettings.HOST).get(query)) == 0:
                        # вставляем новый
                        DBGetter(DBSettings.HOST).insert(
                            "INSERT INTO vk_groups_posts (group_id, group_name, doc_url, type, caption, post_date)"
                            "VALUES (%s, '%s', '%s', 'gifs_with_caption', '%s', %s)" %
                            (vk_group_id, vk_group_name, item["attachments"][0]["doc"]["preview"]["video"]["src"],
                             item["text"], item["date"]))
                        logging.info("Added new 'gifs_with_caption' post with caption: %s and doc_url: %s" %
                                     (item["text"], item["attachments"][0]["doc"]["preview"]["video"]["src"]))
                    else:
                        pass

            except KeyError:
                pass

        # удаляем из БД старые посты,
        # если их общее количество превышает 25
        posts_count = DBGetter(DBSettings.HOST).get("SELECT COUNT(*) FROM vk_groups_posts "
                                                    "WHERE group_id = %s" % vk_group_id)
        if int(posts_count[0][0]) > 25:
            to_delete = int(posts_count[0][0]) - 25
            delete_old_posts = "DELETE FROM vk_groups_posts WHERE ctid IN (SELECT ctid FROM vk_groups_posts " \
                               "WHERE group_id = %s ORDER BY post_date LIMIT %s)" % (vk_group_id, to_delete)
            DBGetter(DBSettings.HOST).insert(delete_old_posts)
            logging.info("Deleted %s posts for group %s" % (to_delete, vk_group_id))

    @staticmethod
    def convert_photo(photo):
        url = photo
        f = open('out.jpg', 'wb')
        f.write(urllib.urlopen(url).read())
        f.close()
        return open('out.jpg', 'rb')

    @staticmethod
    def convert_gif(gif):
        url = gif
        f = open('out.mp4', 'wb')
        f.write(urllib.urlopen(url).read())
        f.close()
        return open('out.mp4', 'rb')

    # asynchronous loading new files to the Telegram servers using the test channel
    def upload_files(self):
        async_bot = telebot.AsyncTeleBot(BotSettings.TOKEN)
        # upload photos
        try:
            photos = DBGetter(DBSettings.HOST).get("SELECT doc_url FROM vk_groups_posts WHERE type IN "
                                                   "('photo_no_caption', 'photo_with_caption') AND file_id IS NULL")
            if len(photos) > 0:
                logging.info("Starting uploading new photos")
                for photo in photos:
                    logging.info("Uploading new photo to the Telegram servers: %s" % photo[0])
                    try:
                        uploading_photo = async_bot.send_photo(chat_id='-1001126259530',
                                                               photo=self.convert_photo("%s" % photo[0]))
                        result = uploading_photo.wait()
                        file_id = result.photo[-1].file_id
                        DBGetter(DBSettings.HOST).insert(
                            "UPDATE vk_groups_posts SET file_id = '%s' WHERE doc_url = '%s'" % (file_id, photo[0]))
                        logging.info("Inserting to DB new photo with file_id: %s" % file_id)
                    except Exception:
                        uploading_photo = async_bot.send_photo(chat_id='-1001126259530',
                                                               photo="%s" % photo[0])
                        result = uploading_photo.wait()
                        file_id = result.photo[-1].file_id
                        DBGetter(DBSettings.HOST).insert(
                            "UPDATE vk_groups_posts SET file_id = '%s' WHERE doc_url = '%s'" % (file_id, photo[0]))
                        logging.info("Inserting to DB new photo with file_id: %s" % file_id)
                logging.info("Count of the new photos uploaded: %s" % len(photos))

            # upload gifs
            gifs = DBGetter(DBSettings.HOST).get("SELECT doc_url FROM vk_groups_posts WHERE type IN "
                                                 "('gifs_no_caption', 'gifs_with_caption') AND file_id IS NULL")
            if len(gifs) > 0:
                logging.info("Starting uploading new gifs")
                for gif in gifs:
                    logging.info("Uploading new gif to the Telegram servers: %s" % gif[0])
                    uploading_gif = async_bot.send_document(chat_id='-1001126259530',
                                                            data=self.convert_gif("%s" % gif[0]))
                    result = uploading_gif.wait()
                    file_id = result.document.file_id
                    DBGetter(DBSettings.HOST).insert("UPDATE vk_groups_posts SET file_id = '%s' "
                                                     "WHERE doc_url = '%s'" % (file_id, gif[0]))
                    logging.info("Inserting to DB new gif with file_id: %s" % file_id)
                logging.info("Count of the new gifs uploaded: %s" % len(gifs))
        except Exception as e:
            logging.error(e)

vk_group_ids = DBGetter(DBSettings.HOST).get("SELECT group_id FROM vk_groups_names")

for group_id in vk_group_ids:
    VKGrabber(APISettings.VK_API_URL).get_vk_groups_news_feed(group_id[0])

VKGrabber(APISettings.VK_API_URL).upload_files()
