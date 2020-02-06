from api import api
from api.user import User

def index(request):
    return api.json_data("Welcome to visit Electronic Ecological Estanciero Server!")

def login(request):
    res, err = api.get_http_arg(request, ("name", "password"))
    if err:
        return api.json_error(err, api.HttpArgumentError)

    user, err = User.get_user(res['name'], res['password'])
    if err:
        return api.json_error(err, api.UserLoginError)

    User.add_online_user(user)

    return api.json_data({"id": user.get_id()})

def logout(request):
    user, err = api.get_online_user_by_request(request)
    if not user:
        return err

    User.del_online_user(user)
    return api.json_data()


def plotform(request):
    user, err = api.get_online_user_by_request(request)
    if not user:
        return err

    return api.json_data({"name": user.name, "plotform": "RaspberryPI"})