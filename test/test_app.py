import flask_jwtlogin as jwtl
from flask import Flask, request
from threading import Thread
from requests import get
import time

app = Flask(__name__)
app.config.update({
    'JWT_HEADER_NAME': 'access-token',
    'JWT_SECRET_KEY': 'you will never guess me',
    'JWT_ENCODING_ALGORITHM': 'HS256'
})
login_manager = jwtl.JWTLogin()
login_manager.init_app(app)
assert all([i in jwtl.JWTLogin().config.values() for i in login_manager.config.values()])  # check singleton and configs


@app.route('/')
def hello():
    return 'Hello world'


@app.route('/jwt/')
@jwtl.jwt_required
def hello_jwt():
    assert app.config.get('JWT_HEADER_NAME') in request.headers
    return 'Succeeded'


def start_app_in_another_thread(app_instance):
    app_instance.run()


if __name__ == '__main__':
    thread = Thread(target=start_app_in_another_thread, args=(app, ))
    thread.start()
    time.sleep(2)
    assert get('http://127.0.0.1:5000/').status_code == 200
    assert get('http://127.0.0.1:5000/').text == 'Hello world'
    assert get('http://127.0.0.1:5000/jwt/').status_code == 401
    assert get('http://127.0.0.1:5000/jwt/', headers={app.config.get('JWT_HEADER_NAME'): 'random'}).status_code == 200
    assert get('http://127.0.0.1:5000/jwt/', headers={app.config.get('JWT_HEADER_NAME'): 'random'}).text == 'Succeeded'

