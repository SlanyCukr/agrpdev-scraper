import pymongo

client = pymongo.MongoClient("mongodb+srv://agrpdev_admin:iTDfSH14l4UA4mAf@arpdev-07wfo.mongodb.net/test?retryWrites=true&w=majority")
db = client.agrpdev
col = db.articles


def insert_articles(articles):
    # find if article is not already in the database, if yes, skip it
    for article in articles:
        articles_in_db = col.find_one({"Link": article.link})
        if not articles_in_db:
            col.insert_one(article.as_dict())
