# api.py
# 封装一些操作，方便views.py使用


from django.http import JsonResponse
from api.user import User


# 错误类型
# code: 错误码
# name: 错误名称
class ApiError:
    def __init__(self, code, name):
        self.code = code
        self.name = name


# 在使用过程中会出现以下的错误
NoError = ApiError(0, "NoError")
HttpArgumentError = ApiError(1, "HttpArgumentError")
UserLoginError = ApiError(2, "UserLoginError")
UserIdError = ApiError(3, "UserIdError")
PlatformNotConnectError = ApiError(4, "PlatformNotConnectError")


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
                err = "POST/GET request: argument `%s` is needed" % arg
                res = None
                break

    return res, err


# 通过http request指定的userid参数作为id，并返回在指定id的在线用户
# 如果不存在该用户，返回(None, 错误描述的JsonResponse对象)
# 否则返回(User, None)
#
# 该函数的用途是在每一个需要登录的请求发生时，检查用户是否登录
def get_online_user_by_request(request):
    res, err = get_http_arg(request, ("userid", ))
    if err:
        return None, json_error(err, HttpArgumentError)

    user = User.get_online_user_by_id(res["userid"])
    if not user:
        return None, json_error("no such user id '%s'" % res["userid"], UserIdError)
    return user, None


# 返回一个json数据包
# json的格式是：
#   {"data": data, "message": message, "code": code}
#   "data"为本次传输具体的数据
#   "message"为返回状态描述，如果成功，值为"OK", 失败为错误名
#   "code"为错误码，0表示没有错误，非零表示出现了错误
#   如果出现了错误，"data"为{"details": 错误描述信息}
#  
#   所有的json数据都是以上的格式
def json_data(data={}, message="OK", code=0):
    return JsonResponse({"data": data, "message": message, "code": code})


# 对json_data做封装，返回一个错误
def json_error(details="", err=NoError):
    return json_data({"details": "error: %s" % details}, err.name, err.code)
