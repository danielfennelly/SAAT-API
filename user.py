from flask_login import UserMixin


class User(UserMixin):
    usersDict = {
        1: {'id': 1, 'name': 'daniel', 'password': '', 'prompt_me': True},
        2: {'id': 2, 'name': 'efrem', 'password': '', 'prompt_me': True}
    }

    def __init__(self, id, name, password, prompt_me=True):
        self.name = name
        self.password = password
        self.id = id
        self.prompt_me = prompt_me  # change this later to user preference

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

    def get_prompt(self):
        return self.prompt_me
