import flask_jwtlogin as jwtl
from flask import Flask, request, jsonify, abort
from threading import Thread
from requests import get, post
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
assert all([i in login_manager.config.values() for i in app.config.values()])  # check singleton and configs


@app.route('/')
def hello():
    """Simple undecorated route"""
    return 'Hello world'


@app.route('/test_anonymous/')
def test_anonymous():
    if jwtl.current_user.is_anonymous:
        abort(403)


@app.route('/jwt/')
@login_manager.jwt_required
def hello_jwt():
    """Sample View with needed jwt in request"""
    assert app.config.get('JWT_HEADER_NAME') in request.headers
    return 'Succeeded'


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown/', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


@app.route('/get-token/<name>')
def get_token(name):
    """Sample view which returns jwt"""
    for i in user_storage:
        if i.name == name:
            return jsonify(login_manager.generate_jwt_token(i.identifier))
    abort(401)


@app.route('/current_user_test/')
@login_manager.jwt_required
def test_current_user():
    return jwtl.current_user.identifier


@app.route('/login/')
@login_manager.jwt_required
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
    for i in user_storage:
        r_get = get('http://127.0.0.1:5000/get-token/{}'.format(i.name))
        token = loads(r_get.text)
        r_login = get('http://127.0.0.1:5000/login/', headers=token)
        assert r_login.text == i.identifier
        current_user_req = get('http://127.0.0.1:5000/current_user_test/', headers=token)
        assert current_user_req.text == i.identifier

    assert get('http://127.0.0.1:5000/test_anonymous/').status_code == 403
    assert get('http://127.0.0.1:5000/').status_code == 200
    assert get('http://127.0.0.1:5000/').text == 'Hello world'
    assert get('http://127.0.0.1:5000/jwt/').status_code == 401
    assert get('http://127.0.0.1:5000/jwt/', headers={app.config.get('JWT_HEADER_NAME'): 'random'}).status_code == 401

    for i in user_storage:
        assert get('http://127.0.0.1:5000/get-token/{}'.format(i.name)).status_code == 200
    assert get('http://127.0.0.1:5000/get-token/Unknown_user').status_code == 401

    for i in user_storage:
        token_json = loads(get('http://127.0.0.1:5000/get-token/{}'.format(i.name)).text)
        user_identifier = get('http://127.0.0.1:5000/login/', headers=token_json).text
        assert i.identifier == user_identifier
    post('http://127.0.0.1:5000/shutdown/')

