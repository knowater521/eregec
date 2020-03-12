from api import api
from api.user import User
from api import config
from api.platform import PlatformServer, Platform
from api.models import UserInfo
from django.http import HttpResponse, StreamingHttpResponse

# 启动平台服务器，监听平台的socket连接
PlatformServer.run_server()


# eregec/api/index
# 测试服务器是否正常工作
def index(request):
    return api.json_data({"details": 'Welcome to visit Electronic Ecological Estanciero Server!'})

def register(request):
    # 请求参数检查
    res, err = api.get_http_arg(request, ('name', 'password'))
    if err:
        return api.json_error(err, api.HttpArgumentError)

    user_info = api.get_user_info_from_database(res['name'])
    if user_info:
        return api.json_error('user {} already exists'.format(res['name']), api.UserAlreadyExistsError)

    user_info = UserInfo()
    user_info.username = res['name']
    user_info.password = res['password']
    user_info.sex = True
    user_info.tel = "13555555555"
    user_info.save()

    return api.json_data()

# eregec/api/login
# 用户登录
# 需要指定POST/GET参数：
#    name: 用户名
#    password: 用户密码
# 返回json数据包：
#    登录成功：
#       "data" 为 {"userid": 用户id}
#    登录失败：错误描述的json数据
def login(request):
    # 请求参数检查
    res, err = api.get_http_arg(request, ('name', 'password'))
    if err:
        return api.json_error(err, api.HttpArgumentError)

    # 创建user对象
    user, err = User.get_user(res['name'], res['password'])
    if err:
        return api.json_error(err, api.UserLoginError)

    # 标记为在线（已登录）
    User.add_online_user(user)

    # 返回userid
    return api.json_data({'userid': user.get_userid()})


# eregec/api/logout
# 用户登出（用户下线）
# POST/GET参数：
#    userid:  用户id
def logout(request):
    # 通过userid获取用户，如果失败，返回错误信息
    user, _, err = api.get_online_user_by_request(request)
    if not user:
        return err

    # 将用户标记为下线
    User.del_online_user(user)

    # 返回成功信息
    return api.json_data()

# eregec/api/platform-data
# 获取平台数据
# POST/GET参数：
#    userid:  用户id
# 返回数据：
# 如果成功，"data"里
#     数据名称: 数据值
#     ...
# 如果失败，返回错误信息
def platform_data(request):
    # 通过userid获取用户，如果失败，返回错误信息
    user, _, err = api.get_online_user_by_request(request)
    if not user:
        return err

    # 要求平台对象，如果没有找到，返回错误信息
    platform = PlatformServer.get_platform_by_name(user.username)
    if not platform:
        return api.json_error("platform not connected!", api.PlatformNotConnectError)

    # 取出平台数据，并返回相关数据
    data, err = platform.get_data()
    if err:
        return api.json_error(err, api.DataFailedError)
    return api.json_data(data)

# eregec/api/platform-info
# 获取平台数据
# POST/GET参数：
#    userid:  用户id
# 返回数据：
# 如果成功，"data"里是平台信息
# 如果失败，返回错误信息
def platform_info(request):
    # 通过userid获取用户，如果失败，返回错误信息
    user, _, err = api.get_online_user_by_request(request)
    if not user:
        return err

    return api.json_data(user.platform_info)

# eregec/api/user-info
# 获取平台数据
# POST/GET参数：
#    userid:  用户id
# 返回数据：
# 如果成功，"data"里是用户信息
# 如果失败，返回错误信息
def user_info(request):
    # 通过userid获取用户，如果失败，返回错误信息
    user, _, err = api.get_online_user_by_request(request)
    if not user:
        return err

    return api.json_data(user.user_info)

# eregec/api/cmd
# 获取平台数据
# POST/GET参数：
#    userid: 用户id
#    string: 命令
# 如果失败，返回错误信息
def cmd(request):
    # 通过userid获取用户，如果失败，返回错误信息
    
    user, res, err = api.get_online_user_by_request(request, ('string', ))
    if not user:
        return err

    # 要求平台对象，如果没有找到，返回错误信息
    platform = PlatformServer.get_platform_by_name(user.name)
    if not platform:
        return api.json_error('platform not connected!', api.PlatformNotConnectError)

    # 执行命令
    res = platform.send_cmd(res['string'])
    if res:
        return api.json_error(res, api.CommandFailedError)
    return api.json_data() 

    

# eregec/api/image
# 获取当前的图片
# POST/GET参数：
#    userid: 用户id
# 如果失败，返回错误信息
def image(request):
    # 通过userid获取用户，如果失败，返回错误信息
    
    user, _, err = api.get_online_user_by_request(request)
    if not user:
        return err

        # 要求平台对象，如果没有找到，返回错误信息
    platform = PlatformServer.get_platform_by_name(user.username)
    if not platform:
        return api.json_error('platform not connected!', api.PlatformNotConnectError)


    # 获取图片
    image = platform.get_image_data()
    return HttpResponse(image, content_type='image/jpg')

# eregec/api/stream
# 获取当前的图片
# POST/GET参数：
#    userid: 用户id
# 如果失败，返回错误信息
def stream(request):
    # 通过userid获取用户，如果失败，返回错误信息
    
    user, _, err = api.get_online_user_by_request(request)
    if not user:
        return err

        # 要求平台对象，如果没有找到，返回错误信息
    platform = PlatformServer.get_platform_by_name(user.username)
    if not platform:
        return api.json_error('platform not connected!', api.PlatformNotConnectError)


    def image_stream():
        while True:
            frame = platform.get_image_data()
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'

    return StreamingHttpResponse(image_stream(), content_type='multipart/x-mixed-replace; boundary=frame')