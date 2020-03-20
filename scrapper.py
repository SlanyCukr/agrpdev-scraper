import scrapy
from ArticleInfo import ArticleInfo


class AgrpSpider(scrapy.Spider):
    name = 'AgrpSpider'
    start_urls = ['https://www.novinky.cz/']

    def parse(self, response):
        urls = []
        titles = []
        recentTitles = []
        recentUrls = []
        for url in response.css('div.f_aH>a.d_aB ::attr(href)'):
            urls.append(url.extract())
        for url in response.css('div.f_bH>a.d_aB ::attr(href)'):
            recentUrls.append(url.extract())
        for title in response.css('h3.d_w.d_z.f_aV ::text'):
            titles.append(title.get())
        for title in response.css('h3.d_w.d_z.f_bT ::text'):
            recentTitles.append(title.get())

        articles = []
        for i in range(len(urls)):
            articles.append(ArticleInfo(urls[i], titles[i], "", "", ""))

        for i in range(len(recentUrls)):
            articles.append(ArticleInfo(recentUrls[i], recentTitles[i], "", "", ""))

        f = open("C:/test.txt", "w", encoding="utf-8")
        for articleInfo in articles:
            f.write(str(articleInfo))

        f = open("C:/urls.txt", "w")

        for url in urls:
            f.write(url + "\n")
        f.close()

        f = open("C:/urls1.txt", "w")

        for url in recentUrls:
            f.write(url + "\n")
        f.close()

        f = open("C:/titles.txt", "w", encoding="utf-8")

        for title in titles:
            f.write(title + "\n")
        f.close()

        f = open("C:/titles1.txt", "w", encoding="utf-8")

        for title in recentTitles:
            f.write(title + "\n")
        f.close()

        #for next_page in response.css('a.next-posts-link'):
            #yield response.follow(next_page, self.parse)