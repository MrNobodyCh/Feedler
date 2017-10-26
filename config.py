# coding=utf-8
import vk_api


class BotSettings:
    # for the tests
    # TOKEN = ""
    # production token
    TOKEN = ""
    COMMANDS = ["/menu", "/subscriptions", "/search", "/top5", "/rate",
                "/vk", "/feedback", "/language", "/donate", "/start"]


class DBSettings:
    HOST = "postgres"


class ResourcesSettings(object):
    def __init__(self, resource):
        self.resource = resource

    RESOURCES = ["tut.by", "onliner.by", "news.mail.ru", "news.yandex.ru", "rambler.ru",
                 "rbc.ru", "lenta.ru", "charter97.org", "udf.by", "belta.by", "korrespondent.net",
                 "obozrevatel.com", "censor.net.ua", "telegraf.com.ua", "edition.cnn.com", "nytimes.com",
                 "theguardian.com", "washingtonpost.com", "bbc.com", "segodnya.ua"]

    TOP_COUNTRIES = ["russia", "belarus", "ukraine", "world"]

    VK_GROUPS_IDS = {"MDK": 57846937, "БОРЩ": 460389,
                     "ЁП": 12382740, "Смейся до слёз :D": 26419239,
                     "Корпорация Зла": 29246653}

    def get_country_by_resource(self):
        if self.resource in ["tut.by", "onliner.by", "charter97.org", "udf.by", "belta.by"]:
            return "belarus"

        if self.resource in ["news.mail.ru", "news.yandex.ru", "rambler.ru", "rbc.ru", "lenta.ru"]:
            return "russia"

        if self.resource in ["segodnya.ua", "korrespondent.net", "obozrevatel.com", "censor.net.ua", "telegraf.com.ua"]:
            return "ukraine"

        if self.resource in ["edition.cnn.com", "nytimes.com", "theguardian.com", "washingtonpost.com", "bbc.com"]:
            return "world"

    def get_categories(self):
        if self.resource == "tut.by":
            return {"Главные новости_%s" % self.resource: "index",
                    "Деньги и власть_%s" % self.resource: "economics",
                    "Общество_%s" % self.resource: "society",
                    "Кругозор_%s" % self.resource: "culture",
                    "В мире_%s" % self.resource: "world",
                    "Происшествия_%s" % self.resource: "accidents",
                    "Финансы_%s" % self.resource: "finance",
                    "Недвижимость_%s" % self.resource: "realty",
                    "Авто_%s" % self.resource: "auto",
                    "Спорт_%s" % self.resource: "sport"}

        if self.resource == "onliner.by":
            return {"Главные новости_%s" % self.resource: "www",
                    "Люди_%s" % self.resource: "people",
                    "Автомобили_%s" % self.resource: "auto",
                    "Технологии_%s" % self.resource: "tech",
                    "Недвижимость_%s" % self.resource: "realt"}

        if self.resource == "edition.cnn.com":
            return {"Top Stories_%s" % self.resource: "edition",
                    "World_%s" % self.resource: "edition_world",
                    "Most Recent_%s" % self.resource: "cnn_latest",
                    "Entertainment_%s" % self.resource: "edition_entertainment",
                    "World Sport_%s" % self.resource: "edition_sport"}

        if self.resource == "nytimes.com":
            return {"HomePage_%s" % self.resource: "HomePage",
                    "World_%s" % self.resource: "World",
                    "Politics_%s" % self.resource: "Politics",
                    "Business_%s" % self.resource: "Business",
                    "Technology_%s" % self.resource: "Technology",
                    "Sports_%s" % self.resource: "Sports",
                    "Science_%s" % self.resource: "Science",
                    "Health_%s" % self.resource: "Health"}

        if self.resource == "theguardian.com":
            return {"Latest_%s" % self.resource: "international",
                    "World_%s" % self.resource: "world",
                    "Sport_%s" % self.resource: "sport",
                    "Culture_%s" % self.resource: "culture",
                    "Lifestyle_%s" % self.resource: "lifeandstyle",
                    "Fashion_%s" % self.resource: "Fashion",
                    "Environment_%s" % self.resource: "environment",
                    "Technology_%s" % self.resource: "technology",
                    "Travel_%s" % self.resource: "travel"}

        if self.resource == "washingtonpost.com":
            return {"Politics_%s" % self.resource: "politics",
                    "Opinions_%s" % self.resource: "opinions",
                    "Local_%s" % self.resource: "local",
                    "Sports_%s" % self.resource: "sports",
                    "National_%s" % self.resource: "national",
                    "World_%s" % self.resource: "world",
                    "Business_%s" % self.resource: "business",
                    "Lifestyle_%s" % self.resource: "lifestyle",
                    "Entertainment_%s" % self.resource: "entertainment"}

        if self.resource == "bbc.com":
            return {"Top Stories_%s" % self.resource: "",
                    "World_%s" % self.resource: "world",
                    "UK_%s" % self.resource: "uk",
                    "Business_%s" % self.resource: "business",
                    "Politics_%s" % self.resource: "politics",
                    "Health_%s" % self.resource: "health",
                    "Education & Family_%s" % self.resource: "education",
                    "Science & Environment_%s" % self.resource: "science_and_environment",
                    "Technology_%s" % self.resource: "technology",
                    "Entertainment & Arts_%s" % self.resource: "entertainment_and_arts"}

        if self.resource == "news.mail.ru":
            return {"Главные новости_%s" % self.resource: "main",
                    "Политика_%s" % self.resource: "politics",
                    "Экономика_%s" % self.resource: "economics",
                    "Общество_%s" % self.resource: "society",
                    "События_%s" % self.resource: "incident",
                    "Спорт_%s" % self.resource: "sport"}

        if self.resource == "news.yandex.ru":
            return {"Главное_%s" % self.resource: "index",
                    "Политика_%s" % self.resource: "politics",
                    "Общество_%s" % self.resource: "society",
                    "Экономика_%s" % self.resource: "business",
                    "В мире_%s" % self.resource: "world",
                    "Спорт_%s" % self.resource: "sport",
                    "Происшествия_%s" % self.resource: "incident",
                    "Культура_%s" % self.resource: "culture",
                    "Технологии и Наука_%s" % self.resource: "computers",
                    "Авто_%s" % self.resource: "auto"}

        if self.resource == "rambler.ru":
            return {"Главное_%s" % self.resource: "head",
                    "В мире_%s" % self.resource: "world",
                    "В Москве_%s" % self.resource: "moscow_city",
                    "Политика_%s" % self.resource: "politics",
                    "Бизнес_%s" % self.resource: "business",
                    "Происшествия_%s" % self.resource: "incidents",
                    "Шоу-бизнес_%s" % self.resource: "starlife",
                    "Спорт_%s" % self.resource: "sport",
                    "Авто_%s" % self.resource: "auto",
                    "Наука_%s" % self.resource: "science",
                    "Технологии_%s" % self.resource: "scitech",
                    "Стиль жизни_%s" % self.resource: "lifestyle"}

        if self.resource == "rbc.ru":
            return {"Все материалы_%s" % self.resource: "news"}

        if self.resource == "segodnya.ua":
            return {"Все материалы_%s" % self.resource: "xml"}

        if self.resource == "lenta.ru":
            return {"Новости_%s" % self.resource: "news",
                    "Самые свежие и самые важные новости_%s" % self.resource: "top7",
                    "Главные новости за последние сутки_%s" % self.resource: "last24"}

        if self.resource == "charter97.org":
            return {"Все Новости_%s" % self.resource: "all",
                    "Политика_%s" % self.resource: "politics",
                    "Европа_%s" % self.resource: "europa",
                    "Культура_%s" % self.resource: "culture",
                    "Религия_%s" % self.resource: "religion",
                    "В мире_%s" % self.resource: "world",
                    "Общество_%s" % self.resource: "society",
                    "Россия_%s" % self.resource: "russia"}

        if self.resource == "udf.by":
            return {"Политика_%s" % self.resource: "politic",
                    "Экономика_%s" % self.resource: "economic",
                    "Общество_%s" % self.resource: "society",
                    "Культура_%s" % self.resource: "kultura",
                    "Технологии_%s" % self.resource: "tech",
                    "В мире_%s" % self.resource: "world",
                    "Спорт_%s" % self.resource: "sport",
                    "Мнение_%s" % self.resource: "commments",
                    "Без галстука_%s" % self.resource: "nopolitic"}

        if self.resource == "belta.by":
            return {"Главные новости_%s" % self.resource: "",
                    "Президент_%s" % self.resource: "president",
                    "Политика_%s" % self.resource: "politics",
                    "Экономика_%s" % self.resource: "economics",
                    "Общество_%s" % self.resource: "society",
                    "Регионы_%s" % self.resource: "regions",
                    "Происшествия_%s" % self.resource: "incident",
                    "Технологии_%s" % self.resource: "tech",
                    "В мире_%s" % self.resource: "world",
                    "Культура_%s" % self.resource: "culture",
                    "Спорт_%s" % self.resource: "sport"}

        if self.resource == "korrespondent.net":
            return {"Все новости_%s" % self.resource: "all_news",
                    "Новости Киева_%s" % self.resource: "kyiv",
                    "Картинка дня_%s" % self.resource: "mainbyday",
                    "Новости бизнеса_%s" % self.resource: "business",
                    "Шоу-Бизнес_%s" % self.resource: "showbiz",
                    "Новости Украины_%s" % self.resource: "ukraine",
                    "Наука и Медицина_%s" % self.resource: "tech",
                    "Новости Спорта_%s" % self.resource: "sport",
                    "Новости Мира_%s" % self.resource: "world",
                    "Lifestyle&Fashion_%s" % self.resource: "lifestyle"}

        if self.resource == "obozrevatel.com":
            return {"Все новости_%s" % self.resource: "",
                    "Политика_%s" % self.resource: "politics",
                    "Общество_%s" % self.resource: "society",
                    "Мир_%s" % self.resource: "abroad",
                    "Экономика_%s" % self.resource: "finance",
                    "Спорт_%s" % self.resource: "sport"}

        if self.resource == "censor.net.ua":
            return {"Все новости_%s" % self.resource: "news_ru",
                    "Резонанс_%s" % self.resource: "resonance_ru",
                    "Фоторепортажи_%s" % self.resource: "photonews_ru",
                    "Видео_%s" % self.resource: "videonews_ru",
                    "События_%s" % self.resource: "events_ru",
                    "Фотошопы политиков_%s" % self.resource: "photoshops_ru",
                    "Анектоды_%s" % self.resource: "jokes_ru",
                    "Форум_%s" % self.resource: "forum_ru"}

        if self.resource == "telegraf.com.ua":
            return {"Все новости_%s" % self.resource: "",
                    "Украина_%s" % self.resource: "ukraina",
                    "Бизнес_%s" % self.resource: "biznes",
                    "Мир_%s" % self.resource: "mir",
                    "Спорт_%s" % self.resource: "sport-cat",
                    "Культура_%s" % self.resource: "kultura",
                    "Жизнь_%s" % self.resource: "zhizn"}


class RssSettings:
    def __init__(self, rss_domain):
        self.rss_domain = rss_domain

    RESOURCES_DOMAINS = []
    for x in ResourcesSettings.RESOURCES:
        RESOURCES_DOMAINS.append("http://" + x)

    def get_full_rss_url(self):
        if self.rss_domain == "http://tut.by":
            return "https://news.tut.by/rss/%s.rss"

        if self.rss_domain == "http://onliner.by":
            return "https://%s.onliner.by/feed"

        if self.rss_domain == "http://edition.cnn.com":
            return "http://rss.cnn.com/rss/%s.rss"

        if self.rss_domain == "http://nytimes.com":
            return "http://rss.nytimes.com/services/xml/rss/nyt/%s.xml"

        if self.rss_domain == "http://theguardian.com":
            return "https://www.theguardian.com/%s/rss"

        if self.rss_domain == "http://washingtonpost.com":
            return "http://feeds.washingtonpost.com/rss/%s"

        if self.rss_domain == "http://bbc.com":
            return "http://feeds.bbci.co.uk/news/%s/rss.xml"

        if self.rss_domain == "http://news.mail.ru":
            return "https://news.mail.ru/rss/%s/"

        if self.rss_domain == "http://news.yandex.ru":
            return "https://news.yandex.ru/%s.rss"

        if self.rss_domain == "http://rambler.ru":
            return "https://news.rambler.ru/rss/%s/"

        if self.rss_domain == "http://rbc.ru":
            return "http://static.feed.rbc.ru/rbc/logical/footer/%s.rss"

        if self.rss_domain == "http://lenta.ru":
            return "https://lenta.ru/rss/%s"

        if self.rss_domain == "http://charter97.org":
            return "https://charter97.org/ru/rss/%s/"

        if self.rss_domain == "http://udf.by":
            return "http://udf.by/all/%s/rss.xml"

        if self.rss_domain == "http://belta.by":
            return "http://www.belta.by/rss/%s/"

        if self.rss_domain == "http://korrespondent.net":
            return "http://k.img.com.ua/rss/ru/%s.xml"

        if self.rss_domain == "http://obozrevatel.com":
            return "https://www.obozrevatel.com/%s/rss.xml"

        if self.rss_domain == "http://censor.net.ua":
            return "https://censor.net.ua/includes/%s.xml"

        if self.rss_domain == "http://telegraf.com.ua":
            return "http://telegraf.com.ua/%s/feed/"

        if self.rss_domain == "http://segodnya.ua":
            return "http://www.segodnya.ua/%s/rss.xml"


class APISettings:
    BOTAN_TOKEN = ""
    GOOGL_TOKEN = ""
    VK_API_URL = vk_api.VkApi(login="", password="")
