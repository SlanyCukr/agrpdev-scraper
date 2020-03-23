import scrapy
import time

from utils.parsers import parse_article_id_url, parse_all_urls, parse_additional_data, parse_comments
from utils.database import insert_articles


class AgrpSpider(scrapy.Spider):
    name = 'AgrpSpider'
    start_urls = ['https://www.novinky.cz/']

    articles = []

    # disable filtering of duplicate pages (it is needed when correcting errors of accessing websites)
    custom_settings = {
        'DEPTH_LIMIT': 3,
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter'
    }

    def closed(self, reason):
        self.logger.info(str(reason))

        for article in self.articles:
            if not article.is_populated():
                self.logger.error(f"Article with link {article.link} is not populated. It can't be resolved here.")

        insert_articles(self.articles)

    def parse(self, response):
        """
        Visits novinky.cz and calculates id of article to visit novinky.cz with
        :param response: Scrapy response
        :return:
        """
        # handle empty date_limit, empty url_limit
        if not hasattr(self, 'date_limit'):
            self.date_limit = None
        if not hasattr(self, 'url_limit'):
            self.url_limit = 20

        url_with_url_limit = parse_article_id_url(response, self.url_limit)

        yield scrapy.Request(url_with_url_limit, callback=self.call_all_urls, errback=self.errback_httpbin)

    def call_all_urls(self, response):
        """
        Creates list of articles URLs and visits them in method parse_additional_data
        :param response: Scrapy response
        :return:
        """
        parse_all_urls(response, self.articles, self.url_limit)

        # retrieve additional data from articles
        for article in self.articles:
            if not article.is_populated():
                yield scrapy.Request(article.link, callback=parse_additional_data, errback=self.errback_httpbin,
                                     dont_filter=True, meta={'article_object': article, 'articles': self.articles, 'date_limit': self.date_limit})

        # retrieve comments from articles
        for article in self.articles:
            yield scrapy.Request(article.comment_link, callback=parse_comments, errback=self.errback_httpbin, dont_filter=True, meta={'article_object': article})

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
            url = failure.value.response.url
        except:
            url = failure.request.url

        self.logger.error(f"Error accessing website {url}, trying again in 1 second.")
        time.sleep(1)

        self.logger.debug(f"Trying to access website {url} again.")

        if url.split('/')[-1].isdigit():
            yield scrapy.Request(url, callback=parse_comments, errback=self.errback_httpbin,
                                 meta={'article_object': next((x for x in self.articles if x.comment_link == url), None)})
        else:
            yield scrapy.Request(url, callback=parse_additional_data, errback=self.errback_httpbin,
                                 meta={'article_object': next((x for x in self.articles if x.link == url), None), 'articles': self.articles, 'date_limit': self.date_limit})
