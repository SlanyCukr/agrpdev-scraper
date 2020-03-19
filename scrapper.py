import scrapy
from scrapy.shell import inspect_response


class AgrpSpider(scrapy.Spider):
    name = 'AgrpSpider'
    start_urls = ['https://www.idnes.cz/', 'https://www.sport.cz/', 'https://www.novinky.cz/']

    def parse(self, response):
        urls = []
        titles = []
        recentTitles = []
        recentUrls = []
        for url in response.css('div.f_aH>a.d_aB ::attr(href)'):
            urls.append(url.extract())
        for url in response.css('div.f_bH>a.d_aB ::attr(href)'):
            recentUrls.append(url.extract())
        for title in response.css('.d_w.d_z.f_aV::text'):
            titles.append(title.get())
        for title in response.css('d_w.d_z.f_bT::text'):
            recentTitles.append(title.get())

        f = open("C:/urls.txt", "w")

        for url in urls:
            f.write(url + "\n")
        f.close()

        f = open("C:/urls1.txt", "w")

        for url in recentUrls:
            f.write(url + "\n")
        f.close()

        f = open("C:/titles.txt", "w")

        for title in titles:
            f.write(title)
        f.close()

        #for next_page in response.css('a.next-posts-link'):
            #yield response.follow(next_page, self.parse)