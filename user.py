from flask_login import UserMixin


class User(UserMixin):
    def __init__(self,user):
        self._user = user
    def __getattr__(self,k):
        try:
            return self._user[k]
        except KeyError:
            raise AttributeError()
    def get_id(self):
        return self._user['id']
