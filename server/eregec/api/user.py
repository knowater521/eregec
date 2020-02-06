# user.py
# 处理用户信息

import os, json
from api import config

_user_id = 0

# 产生一个新的id，保证该id不会与已经在线的用户id一致
# 此id用于区分不同的用户
def get_new_id():
    global _user_id
    _user_id += 1
    return str(100000 + _user_id)

# 用户对象
class User:
    # 保存已经在线的用户
    _online_user = []

    def __init__(self, id, name="", password="", platform=None):
        self.id = id
        self.name = name
        self.password = password
        self.platform = platform

    def __eq__(self, user):
        return self.id == user.id

    # 返回用户id
    def get_id(self):
        return self.id

    # 克隆一个用户对象
    def clone(self):
        user = User("")
        user.id = self.id
        user.name = self.name
        user.password = self.password
        user.platform = self.platform
        return user

    # 将制定用户添加到在线用户列表里，表示该用户已登录
    @staticmethod
    def add_online_user(user):
        if user not in User._online_user:
            User._online_user.append(user.clone())

    # 将指定用户从用户在线列表里移除，表示该用户已下线
    @staticmethod
    def del_online_user(user):
        if user in User._online_user:
            User._online_user.remove(user)

    # 通过id获取已在线的用户对象
    # 如果id不存在，返回None
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

    # 通过用户名和密码创建一个user对象
    # 如果创建失败，返回(None, 错误描述)
    @staticmethod
    def get_user(name, password):
        user, err = None, ""

        user = User.get_online_user_by_name(name)
        if user and user.password != password:
            err = "password error"
            user = None
        elif not user:
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
                            user = User(get_new_id(), name, password, data['platform'])
                except Exception as e:
                    err = "cannot get data of user '%s': %s" % (name, e)
        return user, err
