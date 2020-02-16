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
    def __init__(self, name, id, user_info, platform_info):
        self.name = name
        self.id = id
        self.password = user_info.pop('password', '123456')
        self.user_info = user_info
        self.platform_info = platform_info

    def __eq__(self, user):
        return self.id == user.id

    # 返回用户id
    def get_id(self):
        return self.id

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
    def get_online_user_by_id(id):
        for user in _online_user:
            if user.id == id:
                return user

    @staticmethod
    def get_online_user_by_name(name):
        for user in _online_user:
            if user.name == name:
                return user

    # 通过用户名和密码创建一个user对象
    # 如果创建失败，返回(None, 错误描述)
    @staticmethod
    def get_user(name, password, create_id=True):
        user, err = None, ''

        user = User.get_online_user_by_name(name)
        if user and user.password != password:
            err = 'password error'
            user = None
        elif not user:
            user_file = os.path.join(config.user_data_dir, name + '.user')
            if not os.path.exists(user_file):
                err = 'user "{}" not exists'.format(name)
            else:
                try:
                    with open(user_file) as f:
                        data = json.load(f)
                        user_info = data.get("user", {})
                        platform_info = data.get("platform", {})
                        if  user_info.get('password', '123456') != password:
                            err = "password error"
                        else:
                            userid = _create_new_id() if create_id else name
                            user = User(name, userid, user_info, platform_info)
                except Exception as e:
                    err = 'cannot get data: {}'.format(e)
        return user, err
