import scrapy
from datetime import datetime, timedelta
from ArticleInfo import ArticleInfo
import json


class AgrpSpider(scrapy.Spider):
    name = 'AgrpSpider'
    start_urls = ['https://www.novinky.cz/']

    articles = []

    custom_settings = {
        'DEPTH_LIMIT': 1
    }

    def parse(self, response):
        urls = []

        # load urls from section "top_clanky", and from "stalo-se"
        for url in response.css('div[data-dot="top_clanky"] a::attr(href)'):
            urls.append(url.extract())
        for url in response.css('div[data-dot="stalo_se"] a::attr(href)'):
            urls.append(url.extract())

        # retrieve additional data from
        for url in urls:
            self.logger.info("Url: " + url)
            yield scrapy.Request(url, callback=self.parse_additional_data, dont_filter=True)

    def closed(self, reason):
        self.logger.info(str(reason))

        for article in self.articles:
            self.logger.info(str(article))

    def parse_additional_data(self, response):
        # load almost all required info from script as text, and convert it to JSON
        additional_infos = response.css('script[type="application/ld+json"] ::text').getall()
        first_script_json = json.loads(additional_infos[0])
        second_script_json = json.loads(additional_infos[1])
        
        # load some data to variables
        header = second_script_json["headline"]
        description = second_script_json["description"]

        item_list_element = first_script_json["itemListElement"]
        category = ""
        for list_element in item_list_element:
            if list_element["position"] == 2:
                category = list_element["name"]

        published_at = datetime.strptime(second_script_json["datePublished"], '%Y-%m-%dT%H:%M:%S.%fZ').strftime("%Y-%m-%d %H:%M:%S")
        modified_at = datetime.strptime(second_script_json["dateModified"], '%Y-%m-%dT%H:%M:%S.%fZ').strftime("%Y-%m-%d %H:%M:%S")

        # retrieve author
        author = self.retrieve_author(response)

        # load all paragraphs and filter out ones, that are too short
        paragraphs = response.css('div[data-dot-data=\'{"component":"article-content"}\'] p::text').getall()
        paragraphs = list(filter(lambda x: len(x) >= 10, paragraphs))

        self.articles.append(ArticleInfo(response.request.url, header, description, category, author, published_at, modified_at, paragraphs))

    def retrieve_author(self, response):
        author = response.css('div[data-dot-data=\'{"click":"author"}\']::text').get(default="") + " "
        author_links = response.css('div[data-dot-data=\'{"click":"author"}\'] a::text').getall()

        if len(author_links) == 0:
            author = author[:-1]

        for text in author_links:
            author += text + ","

        author = author[:-1]

        return author
