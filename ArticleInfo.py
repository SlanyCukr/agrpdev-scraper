class ArticleInfo:
    def __init__(self, link, header, author, published_at, paragraphs):
        self.link = link
        self.header = header
        self.category = "" # TODO: extract from link
        self.author = author
        self.published_at = published_at
        self.paragraphs = paragraphs

    def extractCategoryFromLink(self):
        ;



    def __str__(self):
        return f'Link: {self.link}, Header: {self.header}, Category: {self.category}, Author: {self.author}, Published: {self.published_at}, Paragraphs: {self.paragraphs}\n'
