from functools import wraps
from flask_jwtlogin.JWTLogin import JWTLogin
from flask import request, abort


def jwt_required(func):
    """ 
    checks your request headers to contain jwt with specified name
    aborts with 401 Unauthorized if was not found
    :param func: view to decorate   
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not request.headers.get(JWTLogin().config.get('JWT_HEADER_NAME')):
            abort(401)
        return func(*args, **kwargs)
    return decorated_view



