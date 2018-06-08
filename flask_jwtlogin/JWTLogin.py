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

    def __init__(self):
        if not JWTLogin.instance:
            JWTLogin.instance = JWTLogin.__JWTLogin()

    def __getattr__(self, item):
        return getattr(self.instance, item)


