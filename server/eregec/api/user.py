import os, json
from api import config

_user_id = 0

def get_new_id():
    global _user_id
    _user_id += 1
    return str(100000 + _user_id)

class User:
    _online_user = []

    def __init__(self, id, name="", password=""):
        self.id = id
        self.name = name
        self.password = password

    def __eq__(self, user):
        return self.id == user.id

    def get_id(self):
        return self.id

    def clone(self):
        user = User("")
        user.id = self.id
        user.name = self.name
        user.password = self.password
        return user

    @staticmethod
    def add_online_user(user):
        if user not in User._online_user:
            User._online_user.append(user.clone())

    @staticmethod
    def del_online_user(user):
        if user in User._online_user:
            User._online_user.remove(user)

    @staticmethod
    def get_online_user_by_id(id):
        for user in User._online_user:
            if user.id == id:
                return user.clone()

    @staticmethod
    def get_online_user_by_name(name):
        for user in User._online_user:
            if user.name == name:
                return user.clone()

    @staticmethod
    def get_user(name, password):
        user, err = None, ""

        user = User.get_online_user_by_name(name)
        if not user:
            user_file = os.path.join(config.user_data_dir, name + '.user')
            if not os.path.exists(user_file):
                err = "user '%s' is not exists" % name
            else:
                try:
                    with open(user_file) as f:
                        data = json.load(f)
                        if data['password'] != password:
                            err = "password error"
                        else:
                            user = User(get_new_id(), name, password)
                except Exception as e:
                    err = "cannot get data of user '%s': %s" % (name, e)
        return user, err