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
