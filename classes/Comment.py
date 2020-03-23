class Comment:
    def __init__(self, author_text=",", text="", likes="+0", dislikes="-0", time=""):
        splitted_author_text = author_text.split(',')

        self.author = splitted_author_text[0]
        self.city = splitted_author_text[1]
        self.text = text
        self.likes = int(likes[1:])
        self.dislikes = int(dislikes[1:])
        self.ratio = 0 if not self.likes and not self.dislikes else (round(self.likes / abs(self.likes + self.dislikes), 2))
        self.time = time

    def as_dict(self):
        return {'Author': self.author, 'City': self.city, 'Text': self.text, 'Likes': self.likes, 'Dislikes': self.dislikes, 'Ratio': self.ratio, 'Time': self.time}

    @staticmethod
    def as_dicts(comments):
        dicts = []
        for comment in comments:
            dicts.append(comment.as_dict())
        return dicts