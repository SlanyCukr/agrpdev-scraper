import json
from datetime import datetime

from classes.ArticleInfo import ArticleInfo
from utils.utils import can_add_url
from classes.Comment import Comment


def parse_article_id_url(response, url_limit):
    """
    Finds url on novinky.cz with article_id, that satisfies url_limit condition
    :param response: Scrapy response
    :param url_limit:
    :return: URL as str
    """
    # finds first link to article, splits it into subarrays by '-' and takes last element => id of the article
    first_article_id = response.css('div[data-dot="top_clanky"] a::attr(href)')[0].extract().split('-')[-1]

    # calculate article id in the past -> substract (url_limit - 4) why number 4 ?
    # because first 4 articles are not present in the stalo_se timeline
    needed_article_id = int(first_article_id) - abs((int(url_limit) - 4))

    return "https://www.novinky.cz/?timeline-stalose-lastItem=" + str(needed_article_id)


def parse_all_urls(response, articles, url_limit):
    """
    Populates article list with URLs pointing to articles
    :param response: Scrapy response
    :param articles: Articles list
    :param url_limit:
    :return: None
    """
    # load urls from section "top_clanky", and from "stalo-se"
    for url in response.css('div[data-dot="top_clanky"] a::attr(href)'):
        if can_add_url(articles, url_limit, url.extract()):
            articles.append(ArticleInfo(url.extract()))
    for url in response.css('div[data-dot="stalo_se"] a::attr(href)'):
        if can_add_url(articles, url_limit, url.extract()):
            articles.append(ArticleInfo(url.extract()))


def parse_additional_data(response):
    """
    Retrieves additional data about article and saves it to the ArticleInfo object
    :param response: Scrapy response
    :param date_limit: Date limit in '%Y-%m-%d' format
    :return:
    """
    article = response.meta.get('article_object')
    articles = response.meta.get('articles')
    date_limit = response.meta.get('date_limit')

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

    article.published_at = datetime.strptime(second_script_json["datePublished"], '%Y-%m-%dT%H:%M:%S.%fZ')
    article.modified_at = datetime.strptime(second_script_json["dateModified"], '%Y-%m-%dT%H:%M:%S.%fZ')

    # limit articles by date, this is stronger than limit by url_limit
    if date_limit:
        if article.published_at <= datetime.strptime(date_limit, "%Y-%m-%d"):
            articles.remove(article)
            return

    # retrieve author
    article.author = retrieve_author(response)

    # load all paragraphs and filter out ones, that are too short
    paragraphs = response.css('div[data-dot-data=\'{"component":"article-content"}\'] p::text').getall()
    article.paragraphs = list(filter(lambda x: len(x) >= 70, paragraphs))


def retrieve_author(response):
    """
    Retrieves author from article
    :param response: Scrapy response
    :return: Author as str
    """
    author = response.css('div[data-dot-data=\'{"click":"author"}\']::text').get(default="")
    author_links = response.css('div[data-dot-data=\'{"click":"author"}\'] a::text').getall()

    # no space is needed for author_links
    if len(author_links) != 0 and author:
        author = author + " "

    # if there is extra ',' char, remove it
    if ',' in author:
        author = ""

    for text in author_links:
        author += text + ","

    author = author[:-1]

    return author


def parse_comments(response):
    """
    Retrieves comments from article
    :param response: Scrapy response
    :return: Comments as list of Comment objects
    """
    article = response.meta.get("article_object")

    comments = []

    # parses all info about comments from comments page (xpath needed here to better access to elements)
    author_texts = response.xpath("//a[@data-dot='souhlasim']/../../div/div/div/text()").getall()
    texts = response.xpath("//a[@data-dot='souhlasim']/../../../../div/div/text()").getall()
    likes = response.xpath("//a[@data-dot='souhlasim']/span/text()").getall()
    dislikes = response.xpath("//a[@data-dot='nesouhlasim']/span/text()").getall()
    times = response.xpath("//a[@data-dot='souhlasim']/../../div/div/div/span/text()").getall()

    for i in range(len(likes)):
        comments.append(Comment(author_texts[i], texts[i], likes[i], dislikes[i], times[i]))

    article.comments = comments
