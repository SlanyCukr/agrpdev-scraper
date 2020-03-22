from classes.ArticleInfo import ArticleInfo
from utils.database import retrieve_articles


def can_add_url(articles, url_limit, url=""):
    """
    Checks if url can be added. (if url_limit is not exceeded and if url points to article)
    :param articles: Articles list
    :param url_limit: url_limit as str
    :param url: Url as string
    :return: boolean
    """
    if len(articles) < int(url_limit) and 'timeline-stalose-lastItem' not in url:
        return True
    return False


def find_words(articles):
    """
    Finds all words in all articles
    :param articles: Articles as ArticleInfo objects
    :return: List of all words
    """
    words = []
    for article in articles:
        words.extend(article.words_in_all_paragraphs())

    return words


def retrieve_all_articles():
    """
    Retrieves all articles and converts them to ArticleInfo objects in list
    :return: List of ArticleInfo instances
    """
    articles_db = retrieve_articles(0)
    return ArticleInfo.db_objects_to_articles(articles_db)
