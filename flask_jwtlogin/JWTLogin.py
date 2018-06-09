from flask import request
from flask_jwtlogin.errors import UserLoaderNotSetException
from flask_jwtlogin import AnonymousUser
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
            options:\nJWT_HEADER_NAME\nJWT_SECRET_KEY\nJWT_ENCODING_ALGORITHM"""
            self.current_app = app
            self.config.update(app.config)

        def user_loader(self, callback_func):
            """set callback for loading user from your storage"""
            self._callback = callback_func

        # def load_user(self, identifier: str):
        #     with self.current_app.app_context:
        #         if not self._callback:
        #             raise UserLoaderNotSetException("User loader callback was not set")
        #         token = request.headers.get(self.config.get("JWT_HEADER_NAME"))
        #         if not token:
        #             return AnonymousUser
        #         try:
                    
        def generate_jwt_token(self, identifier: str) -> dict:
            """
            generating jwt token, works only inside application context
            :param identifier: string representing unique identifier of your user 
            :return: dict with structure {"JWT_HEADER_NAME": "your_jwt_token"}  
            """
            with self.current_app.app_context:
                token = jwt.encode({"id": identifier.encode()},
                                   self.config.get("JWT_SECRET_KEY"),
                                   algorithm=self.config.get("JWT_ENCODING_ALGORITHM"))
                return {self.config.get('JWT_HEADER_NAME'): token}

    def __init__(self):
        if not JWTLogin.instance:
            JWTLogin.instance = JWTLogin.__JWTLogin()

    def __getattr__(self, item):
        return getattr(self.instance, item)


