from functools import wraps
from flask_jwtlogin.JWTLogin import JWTLogin
from flask import request, abort, has_request_context


def jwt_required(func):
    """ 
    checks your request headers to contain jwt with specified name
    aborts with 401 Unauthorized if token was not found
    :param func: view to decorate
    :raises RuntimeError if working outside request context
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if has_request_context():  # to work only inside request context
            if not request.headers.get(JWTLogin().config.get('JWT_HEADER_NAME')):
                abort(401)
        else:
            raise RuntimeError("Working outside of request context")
        return func(*args, **kwargs)
    return decorated_view





