from flask import request, has_request_context, abort, g
from flask_jwtlogin.errors import UserLoaderNotSetException
from flask_jwtlogin.users import AnonymousUser, KnownUser, current_user
import time
from functools import wraps
import jwt


class JWTLogin:
    """main class of package, stores configuration &"""
    def __init__(self):
        self.config = dict()
        self._callback = None
        self.current_app = None

    def init_app(self, app):
        """importing configuration from your app\nConfig 
        options:\nJWT_HEADER_NAME\nJWT_SECRET_KEY\nJWT_ENCODING_ALGORITHM\nJWT_LIFETIME"""
        self.current_app = app
        self.config.update(app.config)

    def user_loader(self, callback_func):
        """set callback for loading user from your storage"""
        self._callback = callback_func

    def load_user(self):
        """loads user from jwt in present current request 
        :return AnonymousUser if token isn't present in request or some errors occurred during token decoding
        :return Your user class which extends KnownUser if validation and loading succeeded
        :raises UserLoaderNotSetException if callback function to load user was not set
        :raises RuntimeError if working outside request context 
        """
        if has_request_context():
            if not self._callback:  # callback should be set for correct user loading
                raise UserLoaderNotSetException("User loader callback was not set")
            token = self.get_jwt()
            if not token:
                return AnonymousUser()
            try:
                decoded_token = jwt.decode(token, key=self.config.get("JWT_SECRET_KEY"),
                                           algorithm=self.config.get("JWT_ENCODING_ALGORITHM"))
                user = self._callback(decoded_token.get('sub'))
                return user if user else AnonymousUser()
            except jwt.InvalidTokenError:
                return AnonymousUser()
        raise RuntimeError("Working outside request context")

    def jwt_required(self, func):
        """ 
        checks your request headers to contain jwt with specified name, loads user if jwt is present
        aborts with 401 Unauthorized if token was not found or token 'sub' doesn't represent existing user
        :param func: view to decorate
        :raises RuntimeError if working outside request context
        """
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if has_request_context():  # to work only inside request context
                if not request.headers.get(self.config.get('JWT_HEADER_NAME')):
                    abort(401)
                user = self.load_user()
                if user.is_anonymous():
                    abort(401)
                g._user = user
            else:
                raise RuntimeError("Working outside of request context")
            return func(*args, **kwargs)
        return decorated_view

    def get_jwt(self) -> str:
        """
        Gets jwt from current request, works only inside request context
        :return jwt from current request (if present)
        :raises RuntimeError if working outside request context 
        """
        if has_request_context():
            return request.headers.get(self.config.get("JWT_HEADER_NAME"))
        raise RuntimeError("Working outside request context")

    def generate_jwt_token(self, identifier: str) -> dict:
        """
        generating jwt token, works only inside request context\n
        default PyJWT encoder returns jwt in bytes type which is\n
        not JSON serializable by Flask, so function decodes token to string\n 
        :param identifier: string representing unique identifier of your user 
        :return: dict with structure {"JWT_HEADER_NAME": "your_jwt_token"}
        :raises RuntimeError if working outside request context 
        """
        if has_request_context():
            token = jwt.encode({"sub": identifier,
                                "iat": int(time.time()),
                                "exp": int(time.time()) + self.config.get("JWT_LIFETIME")},
                               self.config.get("JWT_SECRET_KEY"),
                               algorithm=self.config.get("JWT_ENCODING_ALGORITHM"))
            return {self.config.get('JWT_HEADER_NAME'): token.decode()}
        raise RuntimeError("Working outside request context")




