from flask_login import UserMixin


class User(UserMixin):
    usersDict = {
        1: {'id': 1, 'name': 'daniel', 'password': ''},
        2: {'id': 2, 'name': 'efrem', 'password': ''}
    }

    def __init__(self, id, name, password):
        self.name = name
        self.password = password
        self.id = id

    def __repr__(self):
        return "<user {}>".format(self.id)

    @classmethod
    def get(cls, uid):
        try:
            uid = int(uid)
        except Exception:
            return

        if uid in cls.usersDict:
            return cls(**cls.usersDict[uid])

    @classmethod
    def validate(cls, name, password):
        for u in cls.usersDict.values():
            if (u["name"] == name) and (u["password"] == password):
                return cls.get(u["id"])

    def get_id(self):
        return str(self.id)
