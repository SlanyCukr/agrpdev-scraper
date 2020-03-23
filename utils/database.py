import pymongo

client = pymongo.MongoClient("mongodb+srv://agrpdev_admin:iTDfSH14l4UA4mAf@arpdev-07wfo.mongodb.net/test?retryWrites=true&w=majority")
db = client.agrpdev
col = db.articles


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


def retrieve_articles(articles_count):
    """
    Retrieve articles from database
    :param articles_count: number of articles to be returned, 0 means all
    :return: Articles as list of dict
    """
    return list(col.find(projection={"_id": 0}, limit=articles_count))


def retrieve_newest_articles(articles_count):
    """
    Return only n newest articles
    :param articles_count: number of articles to be returned, 0 means all
    :return: Articles as list of dict
    """
    return list(col.find(projection={"_id": 0}, limit=articles_count).sort("Published_at", -1))
