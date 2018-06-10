from flask import request
from flask_jwtlogin.errors import UserLoaderNotSetException
from flask_jwtlogin.userMixins import AnonymousUser, KnownUser
import time
import jwt


class JWTLogin:
    instance = None

    class __JWTLogin:
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
            :raise UserLoaderNotSetException if callback function to load user was not set
            """
            with self.current_app.app_context():
                if not self._callback:
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

        def get_jwt(self) -> str:
            """
            Gets jwt from current request, works only inside application context
            :return: jwt from current request (if present) 
            """
            with self.current_app.app_context:
                return request.headers.get(self.config.get("JWT_HEADER_NAME"))

        def generate_jwt_token(self, identifier: str) -> dict:
            """
            generating jwt token, works only inside application context
            :param identifier: string representing unique identifier of your user 
            :return: dict with structure {"JWT_HEADER_NAME": b"your_jwt_token"}  
            """
            with self.current_app.app_context():
                token = jwt.encode({"sub": identifier,
                                    "iat": int(time.time()),
                                    "exp": int(time.time()) + self.config.get("JWT_LIFETIME")},
                                   self.config.get("JWT_SECRET_KEY"),
                                   algorithm=self.config.get("JWT_ENCODING_ALGORITHM"))
                return {self.config.get('JWT_HEADER_NAME'): token}

    def __init__(self):
        if not JWTLogin.instance:
            JWTLogin.instance = JWTLogin.__JWTLogin()

    def __getattr__(self, item):
        return getattr(self.instance, item)


