import scrapy
from ArticleInfo import ArticleInfo


class AgrpSpider(scrapy.Spider):
    name = 'AgrpSpider'
    start_urls = ['https://www.novinky.cz/']

    def parse(self, response):
        urls = []
        for url in response.css('div[data-dot="top_clanky"] a::attr(href)'):
            urls.append(url.extract())
        for url in response.css('div[data-dot="stalo_se"] a::attr(href)'):
            urls.append(url.extract())

        for url in urls:
            self.logger.info("Url: " + url)

        #for next_page in response.css('a.next-posts-link'):
            #yield response.follow(next_page, self.parse)