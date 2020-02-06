from django.http import JsonResponse

from api.user import User

class ApiError:
    def __init__(self, code, message):
        self.code = code
        self.message = message

NoError = ApiError(0, "NoError")
HttpArgumentError = ApiError(1, "HttpArgumentError")
UserLoginError = ApiError(2, "UserLoginError")
UserIdError = ApiError(2, "UserIdError")

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

def get_online_user_by_request(request):
    res, err = get_http_arg(request, ("userid", ))
    if err:
        return None, json_error(err, HttpArgumentError)

    user = User.get_online_user_by_id(res["userid"])
    if not user:
        return None, json_error("no such user id '%s'" % res["userid"], HttpArgumentError)
    return user, None

def json_data(data={}, message="ok", code=0):
    return JsonResponse({"data": data, "message": message, "code": code})

def json_error(details="", err=NoError):
    return json_data({"details": "error: %s" % details}, err.message, err.code)



#############################################################################################