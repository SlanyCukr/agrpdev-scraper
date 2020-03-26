from classes.ArticleInfo import ArticleInfo

import pymongo
import timeit

client = pymongo.MongoClient("mongodb+srv://agrpdev_admin:iTDfSH14l4UA4mAf@arpdev-07wfo.mongodb.net/test?retryWrites=true&w=majority")
db = client.agrpdev
col = db.articles

cached_articles = []


def load_to_cache():
    """
    Returns current articles as list of ArticleInfo objects, sorted by date
    :return:
    """
    db_articles = list(col.find(projection={"_id": 0}, limit=0).sort("Published_at", -1))
    return ArticleInfo.db_objects_to_articles(db_articles)


def update_cache():
    """
    Updates cache by searching database for new articles
    :return: None
    """
    global cached_articles
    newest_article = cached_articles[0]
    db_articles = list(col.find({"Published_at": {"$gt": newest_article.published_at}}, projection={"_id": 0}).sort("Published_at", -1))
    articles = ArticleInfo.db_objects_to_articles(db_articles)
    cached_articles = articles + cached_articles


def insert_articles(articles):
    """
    Inserts articles
    :param articles: Articles as ArticleInfo object
    :return: None
    """
    # find if article is not already in the database, if yes, update it
    for article in articles:
        article_in_db = col.find_one({"Link": article.link})
        if not article_in_db:
            col.insert_one(article.as_dict())
        else:
            col.update_one(article_in_db, {"$set": article.as_dict()})


def retrieve_newest_articles():
    """
    Return only n newest articles
    :param articles_count: number of articles to be returned, 0 means all
    :return: Articles as list of dict
    """
    start = timeit.default_timer()
    global cached_articles
    if len(cached_articles) == 0:
        cached_articles = load_to_cache()
    else:
        update_cache()
    stop = timeit.default_timer()

    file1 = open("times.txt", "a")
    file1.write(f"Runtime: {stop - start}.")
    file1.close()

    return cached_articles
