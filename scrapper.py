import scrapy
from ArticleInfo import ArticleInfo


class AgrpSpider(scrapy.Spider):
    name = 'AgrpSpider'
    start_urls = ['https://www.novinky.cz/']

    articles = []

    custom_settings = {
        'DEPTH_LIMIT': 1
    }

    def parse(self, response):
        urls = []
        for url in response.css('div[data-dot="top_clanky"] a::attr(href)'):
            urls.append(url.extract())
        for url in response.css('div[data-dot="stalo_se"] a::attr(href)'):
            urls.append(url.extract())

        for url in urls:
            self.logger.info("Url: " + url)
            yield scrapy.Request(url, callback=self.parse_additional_data, dont_filter=True)

    def parse_additional_data(self, response):
        title = response.css('main h1::text').get()
        self.logger.info("Title: " + title)

        # additional information about the author
        #author = response.css('div[data-dot-data=\'{"component":"mol-author"}\']::text').get(default="").partition('-')[0][1:] + ","
        author = response.css('div[data-dot-data=\'{"click":"author"}\']::text').get(default="") + " "
        links_text = response.css('div[data-dot-data=\'{"click":"author"}\'] a::text').getall()

        if len(links_text) == 0:
            author = author[:-1]

        for text in links_text:
            author += text + ","

        author = author[:-1]

        self.logger.info("Author: " + author)

        