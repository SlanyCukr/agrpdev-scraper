from flask import Flask, request, jsonify


from utils.database import retrieve_articles
from utils.utils import find_words, retrieve_all_articles

app = Flask(__name__)

# this is false, because otherwise jsonify produces weird characters
app.config['JSON_AS_ASCII'] = False


@app.route('/grab_newest_articles', methods=['GET'])
def grab_newest_articles():
    articles_count = int(request.args.get("len"))

    return jsonify(retrieve_articles(articles_count))


@app.route('/grab_longest_words', methods=['GET'])
def grab_longest_words():
    words_count = int(request.args.get("len"))

    articles = retrieve_all_articles()

    # finds all words in all paragraphs and sorts them based on their length
    unsorted_words = find_words(articles)
    sorted_words = sorted(unsorted_words, key=len)

    return jsonify(sorted_words[-words_count:])


@app.route('/grab_most_common_words', methods=['GET'])
def grab_most_common_words():
    words_count = int(request.args.get("len"))
    word_len = int(request.args.get("word_len"))

    articles = retrieve_all_articles()

    # find all words in all articles paragraphs, discard short ones
    unsorted_words = find_words(articles)
    unsorted_words = list(filter(lambda x: len(x) >= word_len, unsorted_words))

    # fills counted_words list with tuples => ("word", occurrence_count)
    counted_words = []
    while len(unsorted_words) != 0:
        word = unsorted_words[0]
        occurrence_count = unsorted_words.count(word)
        counted_words.append((word, occurrence_count))

        unsorted_words = list(filter(lambda x: x != word, unsorted_words))

    # sorts this list by occurrence_count
    counted_words_sorted = sorted(counted_words, key=lambda tup: tup[1])

    return jsonify(counted_words_sorted[-words_count:])


@app.route('/covid_analysis', methods=['GET'])
def covid_analysis():
    articles = retrieve_all_articles()

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
