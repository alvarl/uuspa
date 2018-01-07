from flask_login import UserMixin

class User(UserMixin):

    def __init__(self, id, username, name, surname, password):
        self.id = id
        self.username = username
        self.name = name
        self.surname = surname
        self.password = password

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.name, self.password)