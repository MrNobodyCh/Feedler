# -*- coding: utf-8 -*-
import time
import json
import psycopg2
import requests
import feedparser
from feedfinder2 import find_feeds
from config import APISettings, DBSettings


class GooGl:
    def __init__(self):
        self.access_token = APISettings.GOOGL_TOKEN

    def short_link(self, long_link):
        post_url = 'https://www.googleapis.com/urlshortener/v1/url?key=%s' % self.access_token
        payload = {'longUrl': long_link}
        headers = {'content-type': 'application/json'}
        r = requests.post(post_url, data=json.dumps(payload), headers=headers)
        try:
            return r.json()["id"]
        except KeyError:
            return long_link


class RssParser(object):
    def __init__(self, url):
        self.feed = feedparser.parse(url)

    def get_news_for_known_resource(self):
        news_feed = []
        try:
            news_feed += [(i["title"], i["link"],
                           int(time.mktime(i['published_parsed'])) + 10800)
                          for i in self.feed["entries"]]
        # the case when 'published_parsed' missed or None, then generate desc timestamp for each news
        except (KeyError, TypeError):
            second = 0
            for i in self.feed["entries"]:
                second += 1
                news_feed.append([i["title"], i["link"], int(time.time()) - second])
        return sorted(news_feed, key=lambda x: x[2], reverse=True)[:10]


class RssFinder(object):
    def __init__(self, url):
        self.site = url

    def find_feeds(self):
        feeds_titles = []
        feeds = find_feeds(self.site)
        for feed in feeds:
            f = RssParser(feed).feed
            feeds_titles.append([f['feed'].get('title', '(NO TITLE)'), feed])
        return feeds_titles


class DBGetter(object):
    def __init__(self, dbname):
        self.connection = psycopg2.connect(dbname=dbname)
        self.cur = self.connection.cursor()

    def insert(self, execution, values=None):
        self.cur.execute(execution, values)
        self.connection.commit()
        self.cur.close()
        self.connection.close()

    def get(self, execution):
        self.cur.execute(execution)
        rows = self.cur.fetchall()
        self.cur.close()
        self.connection.close()
        return rows


def texts(user):
    try:
        language = DBGetter(DBSettings.HOST).get("SELECT language FROM user_language WHERE user_id = %s" % user)[0][0]
    except IndexError:
        from texts import english_texts as text
        return text
    if language == "russian":
        from texts import russian_texts as text
        return text
    if language == "english":
        from texts import english_texts as text
        return text
