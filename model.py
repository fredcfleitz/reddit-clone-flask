from flask_login import UserMixin

class comment:
    def __init__(self, id, parent, content, user, score):
        self.id = id
        self.is_authenticated
        self.content = content
        self.user = user
        self.score = score

class User(UserMixin):
    def __init__(self, userName, password):
        self.userName = userName
        self.password = password
    def get_id(self):
        return(self.userName)
