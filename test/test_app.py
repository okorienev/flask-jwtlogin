import flask_jwtlogin as jwtl
from flask import Flask, request, jsonify
from threading import Thread
from requests import get
from json import loads
import time

app = Flask(__name__)
app.config.update({
    'JWT_HEADER_NAME': 'access-token',
    'JWT_SECRET_KEY': 'you will never guess me',
    'JWT_ENCODING_ALGORITHM': 'HS256',
    'JWT_LIFETIME': 3600 * 24 * 7
})
login_manager = jwtl.JWTLogin()
login_manager.init_app(app)
assert all([i in jwtl.JWTLogin().config.values() for i in login_manager.config.values()])  # check singleton and configs


@app.route('/')
def hello():
    """Simple undecorated route"""
    return 'Hello world'


@app.route('/jwt/')
@jwtl.jwt_required
def hello_jwt():
    """Sample View with needed jwt in request"""
    assert app.config.get('JWT_HEADER_NAME') in request.headers
    return 'Succeeded'


@app.route('/get-token/<name>')
def get_token(name):
    """Sample view which returns jwt"""
    for i in user_storage:
        if i.name == name:
            return jsonify(login_manager.generate_jwt_token(i.identifier))
    return 'User not found'


@app.route('/login/')
@jwtl.jwt_required
def login():
    """View that loads user from jwt present in request"""
    user = login_manager.load_user()
    return user.identifier


def start_app_in_another_thread(app_instance):
    app_instance.run()


class User(jwtl.KnownUser):
    """Example of class representing user"""
    def __init__(self, name, age, identifier):
        self.name = name
        self.age = age
        self.identifier = identifier

user_storage = [
    User("Tom", 22, "AF5F123"),
    User("Jim", 25, "FFF1832"),
    User("Peter", 18, "CB0CA931")]


@login_manager.user_loader
def load_user(identifier):
    """example of user loader function"""
    for i in user_storage:
        if i.identifier == identifier:
            return i


if __name__ == '__main__':
    thread = Thread(target=start_app_in_another_thread, args=(app, ))
    thread.start()
    time.sleep(2)
    assert get('http://127.0.0.1:5000/').status_code == 200
    assert get('http://127.0.0.1:5000/').text == 'Hello world'
    assert get('http://127.0.0.1:5000/jwt/').status_code == 401
    assert get('http://127.0.0.1:5000/jwt/', headers={app.config.get('JWT_HEADER_NAME'): 'random'}).status_code == 200
    assert get('http://127.0.0.1:5000/jwt/', headers={app.config.get('JWT_HEADER_NAME'): 'random'}).text == 'Succeeded'
    for i in user_storage:
        assert get('http://127.0.0.1:5000/get-token/{}'.format(i.name)).status_code == 200
    assert get('http://127.0.0.1:5000/get-token/Unknown_user').text == 'User not found'
    for i in user_storage:
        token_json = loads(get('http://127.0.0.1:5000/get-token/{}'.format(i.name)).text)
        user_identifier = get('http://127.0.0.1:5000/login/', headers=token_json).text
        assert i.identifier == user_identifier

