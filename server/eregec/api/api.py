# api.py
# 封装一些操作，方便views.py使用

from django.http import JsonResponse
from api.models import UserData, UserInfo, Data, PlatformInfo, Command
from utils import *


# 产生一个新的id，保证该id不会与已经在线的用户id一致
# 此id用于区分不同的用户
__user_id = 0
def __create_new_id():
    global __user_id
    __user_id += 1
    return str(100000 + __user_id)

# 错误类型
# code: 错误码
# name: 错误名称
class ApiError:
    __code = 0
    def __init__(self, name):
        self.code = ApiError.__code
        self.name = name
        ApiError.__code += 1


# 在使用过程中会出现以下的错误
NoError = ApiError("NoError")
HttpArgumentError = ApiError("HttpArgumentError")
UserLoginError = ApiError("UserLoginError")
UserIdError = ApiError("UserIdError")
PlatformNotConnectError = ApiError("PlatformNotConnectError")
DataFailedError = ApiError("DataFailedError")
CommandFailedError = ApiError("CommandFailedError")
UserAlreadyExistsError = ApiError("UserAlreadyExistsError")
DataError = ApiError("DataError")

# 从http request里的POST/GET请求里取出args里指定的参数
#
# args是一个列表/元组，如('name', 'password')
# 先在POST里取每一个参数，如果没有，在GET里取，如果还没有返回(None, 错误描述)
#
# 返回类型：(map, str)
# map键-值是参数-参数值，如果失败，返回None，str为错误描述
def get_http_arg(request, args):
    res, err = {}, ""

    for arg in args:
        res[arg] = request.POST.get(arg)
        if res[arg] is None:
            res[arg] = request.GET.get(arg)
            if res[arg] is None:
                err = "POST/GET request: missing '{}'".format(arg)
                res = None
                break

    return res, err

def database_init():
    try:
        UserData.objects.all().delete()
        Command.objects.all().delete()
    except Exception as e:
        pwarning('database init falied: {}'.format(e))
        pinfo('please try: ')
        pinfo('    python3 manage.py makemigrations')
        pinfo('    python3 manage.py migrate')

def database_get(table, **kwargs):
    try:
        return table.objects.get(**kwargs)
    except:
        return None

def get_user_info_from_db(username):
    return database_get(UserInfo, username=username)

def get_user_data_from_db(username):
    return database_get(UserData, username=username)

def get_platform_info_from_db(username):
    return database_get(PlatformInfo, username=username)

def create_user_data(username, password):
    user_data = get_user_data_from_db(username)
    if user_data:
        return user_data, ''
    user_info = get_user_info_from_db(username)
    if not user_info:
        return None, 'user `{}` not exists'.format(username)
    else:
        if user_info.password != password:
            return None, 'password of user `{}` error'.format(username)
        else:
            user_data = UserData()
            user_data.username = username
            user_data.userid = __create_new_id()
            user_data.save()
    return user_data, ''

def platform_info_to_json(platform_info):
    return {
        'username': platform_info.username,
        'name': platform_info.name,
    }

def user_info_to_json(user_info):
    return {
        'username': user_info.username,
        'name': user_info.name,
        'sex': user_info.sex,
        'tel': user_info.tel,
    }

def send_command(username, command):
    command_data = Command()
    command_data.username = username
    command_data.value = command
    command_data.save()

# 通过http request指定的userid参数作为id，并返回在指定id的在线用户
# 如果不存在该用户，返回(None, 错误描述的JsonResponse对象)
# 否则返回(UserData, None)
#
# 该函数的用途是在每一个需要登录的请求发生时，检查用户是否登录
def get_online_user_by_request(request, args=()):
    res, err = get_http_arg(request, ('userid', ) + args)
    if err:
        return None, None, json_error(err, HttpArgumentError)

    user_data = database_get(UserData, userid=res['userid'])
    if not user_data:
        return None, res, json_error('no such user id', UserIdError)
    return user_data, res, None

# 返回一个json数据包
# json的格式是：
#   {"data": data, "message": message, "code": code}
#   "data"为本次传输具体的数据
#   "message"为返回状态描述，如果成功，值为"OK", 失败为错误名
#   "code"为错误码，0表示没有错误，非零表示出现了错误
#   如果出现了错误，"data"为{"details": 错误描述信息}
#  
#   所有的json数据都是以上的格式
def json_data(data, message, code):
    return JsonResponse({'data': data, 'message': message, 'code': code}, json_dumps_params={'ensure_ascii': False})

def json_ok(data={}):
    return json_data(data, 'OK', 0)

# 对json_data做封装，返回一个错误
def json_error(details='', err=NoError):
    return json_data({'details': details}, err.name, err.code)