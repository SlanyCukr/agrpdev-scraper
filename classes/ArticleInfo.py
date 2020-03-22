class ArticleInfo:
    def __init__(self, link, header="", description="", category="", author="", published_at="", modified_at="", paragraphs=""):
        self.link = link
        self.header = header
        self.description = description
        self.category = category
        self.author = author
        self.published_at = published_at
        self.modified_at = modified_at
        self.paragraphs = paragraphs

    def is_populated(self):
        if not self.header:
            return False
        return True

    def __str__(self):
        return f'Link: {self.link}\nHeader:{self.header}\nDescription: {self.description}\nCategory: {self.category}\n' \
               f'Author: {self.author}\nPublished: {self.published_at}\nModified_at: {self.modified_at}' \
               f'\nParagraphs count: {len(self.paragraphs)}\n'

    def as_dict(self):
        return {'Link': self.link, 'Header': self.header, 'Description': self.description, 'Category': self.category,
                'Author': self.author, 'Published_at': self.published_at, 'Modified_at': self.modified_at,
                'Paragraphs': self.paragraphs, 'Paragraphs_count': len(self.paragraphs)}
