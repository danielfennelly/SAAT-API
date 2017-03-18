from flask_login import UserMixin


class User(UserMixin):
    usersDict = {
        1: {'id': 1, 'name': 'daniel', 'password': 'password'},
        2: {'id': 2, 'name': 'efrem', 'password': 'poop'}
    }

    current_id = 3

    def __init__(self, id, name, password):
        self.name = name
        self.password = password
        self.id = id

    def __repr__(self):
        return "<user {}>".format(self.id)

    @classmethod
    def get(cls, uid):
        if uid in cls.usersDict:
            return cls(**cls.usersDict[uid])

    @classmethod
    def add(cls, name, password):
        cls.usersDict.update({
            cls.current_id: {
                "id": cls.current_id,
                "name:": name,
                "password": password
            }
        })
        cls.current_id += 1

    def get_id(self):
        return self.id
