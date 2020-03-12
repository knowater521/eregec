# user.py
# 处理用户信息

import os, json
from api import config, api

__user_id = 0

# 产生一个新的id，保证该id不会与已经在线的用户id一致
# 此id用于区分不同的用户
def _create_new_id():
    global __user_id
    __user_id += 1
    return str(100000 + __user_id)


_online_user = []

# 用户对象
class User:

    # 保存已经在线的用户
    def __init__(self, user_info, platform_info, userid):
        self.username = user_info.username
        self.userid = userid
        self.user_info = user_info
        self.platform_info = platform_info

    def __eq__(self, user):
        return self.userid == user.userid

    # 返回用户id
    def get_userid(self):
        return self.userid

    # 将制定用户添加到在线用户列表里，表示该用户已登录
    @staticmethod
    def add_online_user(user):
        if user not in _online_user:
            _online_user.append(user)

    # 将指定用户从用户在线列表里移除，表示该用户已下线
    @staticmethod
    def del_online_user(user):
        if user in _online_user:
            _online_user.remove(user)

    # 通过id获取已在线的用户对象
    # 如果id不存在，返回None
    @staticmethod
    def get_online_user_by_userid(userid):
        for user in _online_user:
            if user.userid == userid:
                return user

    @staticmethod
    def get_online_user_by_username(username):
        for user in _online_user:
            if user.user_info.username == username:
                return user

    # 通过用户名和密码创建一个user对象
    # 如果创建失败，返回(None, 错误描述)
    @staticmethod
    def get_user(name, password, create_id=True):
        user, err = None, ''

        user = User.get_online_user_by_username(name)
        if user and user.user_info.password != password:
            err = 'password error'
            user = None
        elif not user:
            user_info = api.get_user_info_from_database(name)
            platform_info = api.get_platform_info_from_database(name)
            if not user_info:
                err = 'user {} not exists'.format(name)
            else:
                if user_info.password != password:
                    err = "password error"
                else:
                    userid = _create_new_id() if create_id else name
                    user = User(user_info, platform_info, userid)
        return user, err
