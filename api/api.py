from flask import Flask, request, jsonify
from collections import Counter

from utils.database import retrieve_newest_articles
from classes.Comment import Comment
from classes.ArticleInfo import ArticleInfo

app = Flask(__name__)

# this is false, because otherwise jsonify produces weird characters
app.config['JSON_AS_ASCII'] = False


@app.route('/', methods=['GET'])
def home():
    endpoints = "<h3 align='center'>All endpoints</h3><br/><a href='http://slanycukr.hopto.org:5000/covid_analysis'>Covid_analysis</a><br/>" \
                     "<a href='http://slanycukr.hopto.org:5000/grab_newest_articles?len=3'>Grab_newest_articles</a> (3 articles)<br/>" \
                     "<a href='http://slanycukr.hopto.org:5000/grab_longest_words?len=8'>Grab_longest_words</a> (8 longest words)<br/>" \
                     "<a href='http://slanycukr.hopto.org:5000/grab_most_common_words?len=8&word_len=5'>Grab_most_common_words</a> (8 words, ignore words, that are 5 or less characters long)<br/>" \
                     "<a href='http://slanycukr.hopto.org:5000/grab_best_comments?len=5'>Grab_best_comments</a> (5 comments)<br/>"
    return endpoints


@app.route('/grab_newest_articles', methods=['GET'])
def grab_newest_articles():
    articles_count = 3
    if 'len' in request.args:
        articles_count = int(request.args.get("len"))

    articles = retrieve_newest_articles()[:articles_count]
    articles_for_return = []
    for article in articles:
        articles_for_return.append(article.as_dict())

    return jsonify(articles_for_return)


@app.route('/grab_longest_words', methods=['GET'])
def grab_longest_words():
    words_count = 8
    if 'len' in request.args:
        words_count = int(request.args.get("len"))

    articles = retrieve_newest_articles()
    # finds all words in all paragraphs and sorts them based on their length
    unsorted_words = list(dict.fromkeys(ArticleInfo.find_words(articles)))
    sorted_words = sorted(unsorted_words, key=len)

    return jsonify(sorted_words[-words_count:])


@app.route('/grab_most_common_words', methods=['GET'])
def grab_most_common_words():
    words_count = 8
    if 'len' in request.args:
        words_count = int(request.args.get("len"))

    word_len = 10
    if 'word_len' in request.args:
        word_len = int(request.args.get("word_len"))

    articles = retrieve_newest_articles()

    # find all words in all articles paragraphs, discard short ones
    unsorted_words = ArticleInfo.find_words(articles)
    unsorted_words = list(filter(lambda x: len(x) >= word_len, unsorted_words))

    occurrence_count = Counter(unsorted_words)
    counted_words_sorted = occurrence_count.most_common(words_count)

    # sorts this list by occurrence_count
    counted_words_sorted = sorted(counted_words_sorted, key=lambda tup: tup[1])

    return jsonify(counted_words_sorted)


@app.route('/covid_analysis', methods=['GET'])
def covid_analysis():
    articles = retrieve_newest_articles()

    covid_keywords = ["krize", "zdravotnictví", "nemocnice", "roušek", "rouška", "rouškou", "rouška",
                      "covid-19", "koronavirus", "respirátor", "respirátorů", "karanténa", "karanténu",
                      "dezinfekce", "dezinfekcí", "covid19cz", "respirátory", "koronavirem", "opatření"]

    # counts number of articles and number of times keyword occurs (max 1 for each article)
    article_count = 0
    covid_count = 0
    for article in articles:
        article_count += 1
        for keyword in covid_keywords:
            if keyword in list(filter(lambda x: x.lower(), article.words_in_all_paragraphs())):
                covid_count += 1
                break

    # creates string to return as Response
    return_string = "Analysis of words in articles (maximum 1 occurrence per article).<br/>Words:"
    for keyword in covid_keywords:
        return_string += keyword + ", "
    return_string = return_string[:-2]
    return_string += "<br/>Percentage of occurence: <b>" + str(round(covid_count / article_count, 4) * 100) + "</b> %."
    return return_string


@app.route('/grab_best_comments', methods=['GET'])
def grab_best_comments():
    comment_count = 5
    if 'len' in request.args:
        comment_count = int(request.args.get("len"))

    articles = retrieve_newest_articles()

    # finds all comments and sorts them
    comments = Comment.find_comments(articles)
    sorted_comments = sorted(comments, key=lambda obj: (obj.ratio, obj.likes), reverse=True)

    return jsonify(Comment.as_dicts(sorted_comments[:comment_count]))
