import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from datetime import datetime
from ArticleInfo import ArticleInfo
import json
import time
import socket


class AgrpSpider(scrapy.Spider):
    name = 'AgrpSpider'
    start_urls = ['https://www.novinky.cz/']

    articles = []

    # disable filtering of duplicate pages (it is needed when correcting errors of accessing websites)
    custom_settings = {
        'DEPTH_LIMIT': 2,
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter'
    }

    def closed(self, reason):
        self.logger.info(str(reason))

        for article in self.articles:
            if not article.is_populated():
                self.logger.error(f"Article with link {article.link} is not populated. It can't be resolved here.")
            self.logger.info(str(article))

    def parse(self, response):
        """
        Visits novinky.cz and calculates id of article to visit novinky.cz with
        :param response: Scrapy response
        :return:
        """
        # finds first link to article, splits it into subarrays by '-' and takes last element => id of the article
        first_article_id = response.css('div[data-dot="top_clanky"] a::attr(href)')[0].extract().split('-')[-1]

        # calculate article id in the paspt - substract (url_limit - 4) => 4,
        # because first 4 articles are not present in the stalo_se timeline
        needed_article_id = int(first_article_id) - abs((int(self.url_limit) - 4))

        url_with_url_limit = "https://www.novinky.cz/?timeline-stalose-lastItem=" + str(needed_article_id)

        yield scrapy.Request(url_with_url_limit, callback=self.parse_all_urls, errback=self.errback_httpbin)

    def parse_all_urls(self, response):
        """
        Creates list of articles URLs and visits them in method parse_additional_data
        :param response: Scrapy response
        :return:
        """
        # load urls from section "top_clanky", and from "stalo-se"
        for url in response.css('div[data-dot="top_clanky"] a::attr(href)'):
            if self.can_add_url(url.extract()):
                self.articles.append(ArticleInfo(url.extract()))
        for url in response.css('div[data-dot="stalo_se"] a::attr(href)'):
            if self.can_add_url(url.extract()):
                self.articles.append(ArticleInfo(url.extract()))

        # retrieve additional data from urls
        for article in self.articles:
            if not article.is_populated():
                yield scrapy.Request(article.link, callback=self.parse_additional_data, errback=self.errback_httpbin,
                                     dont_filter=True, meta={'article_object': article})

    def parse_additional_data(self, response):
        """
        Retrieves additional data about article and saves it to the ArticleInfo object
        :param response: Scrapy response
        :return:
        """
        article = response.meta.get('article_object')

        # load almost all required info from script as text, and convert it to JSON
        additional_infos = response.css('script[type="application/ld+json"] ::text').getall()
        first_script_json = json.loads(additional_infos[0])
        second_script_json = json.loads(additional_infos[1])

        # load some data to variables
        article.header = second_script_json["headline"]
        article.description = second_script_json["description"]

        item_list_element = first_script_json["itemListElement"]
        for list_element in item_list_element:
            if list_element["position"] == 2:
                article.category = list_element["name"]

        article.published_at = datetime.strptime(second_script_json["datePublished"], '%Y-%m-%dT%H:%M:%S.%fZ').strftime(
            "%Y-%m-%d %H:%M:%S")
        article.modified_at = datetime.strptime(second_script_json["dateModified"], '%Y-%m-%dT%H:%M:%S.%fZ').strftime(
            "%Y-%m-%d %H:%M:%S")

        # retrieve author
        article.author = self.retrieve_author(response)

        # load all paragraphs and filter out ones, that are too short
        paragraphs = response.css('div[data-dot-data=\'{"component":"article-content"}\'] p::text').getall()
        article.paragraphs = list(filter(lambda x: len(x) >= 10, paragraphs))

    def retrieve_author(self, response):
        """
        Retrieves author from article
        :param response: Scrapy response
        :return:
        """
        author = response.css('div[data-dot-data=\'{"click":"author"}\']::text').get(default="") + " "
        author_links = response.css('div[data-dot-data=\'{"click":"author"}\'] a::text').getall()

        # no space is needed for author_links
        if len(author_links) == 0:
            author = author[:-1]

        # if there is extra ',' char, remove it
        if ',' in author:
            author = ""

        for text in author_links:
            author += text + ","

        author = author[:-1]

        return author

    def can_add_url(self, url=""):
        """
        Checks if url can be added. (if url_limit is not exceeded and if url points to article)
        :param url: Url as string
        :return: boolean
        """
        if len(self.articles) < int(self.url_limit) and 'timeline-stalose-lastItem' not in url:
            return True
        return False

    def errback_httpbin(self, failure):
        """
        Handles errors during scrapping
        :param failure:
        :return:
        """
        # log all failures
        self.logger.error(repr(failure))

        # retrieve url - using try-except block, because we can't tell where url is
        url = ""
        try:
            url = failure.value.response
        except:
            url = failure.request.url

        self.logger.error(f"Error accessing website {url}, trying again in 1 second.")
        time.sleep(1)

        self.logger.debug(f"Trying to access website {url} again.")

        yield scrapy.Request(url, callback=self.parse_additional_data, errback=self.errback_httpbin, meta={'article_object': next((x for x in self.articles if x.link == url), None)})
