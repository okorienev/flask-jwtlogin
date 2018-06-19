# Flask-jwtlogin quickstart
flask-jwtlogin is a lightweight flask extension to handle users in REST APIs  
What it offers to you:
* **jwt_required** decorator to check jwt presence in current request
* **generate_jwt** func to get token with user identifier encrypted
* **load_user** for manual loading user from request using callback function
* **current_user** proxy 

### How to use it?
First of all, you need some configuration:
```python
{
    'JWT_HEADER_NAME': 'your_header_name',  #header to retrieve token from request
    'JWT_SECRET_KEY': 'you will never guess me',  #keep it secret
    'JWT_ENCODING_ALGORITHM': 'HS256',  #look at algorithms present in PyJWT
    'JWT_LIFETIME': 3600 * 24 * 7  # in seconds
}
```
Then create a login manager instance.
```python
login_manager = jwtl.JWTLogin()  #creating instance
login_manager.init_app(app)  #importing configuration
```

You need to set callback function loading users from your storage and to inherit your user class from KnownUser
```python
class User(jwtl.KnownUser):
    """Example of class representing user"""
    def __init__(self, name, age, identifier):
        self.name = name
        self.age = age
        self.identifier = identifier
        
user_storage = [  #sample storage
    User("Tom", 22, "AF5F123"),
    User("Jim", 25, "FFF1832"),
    User("Peter", 18, "CB0CA931")]


@login_manager.user_loader
def load_user(identifier):
    """example of user loader function"""
    for i in user_storage:
        if i.identifier == identifier:
            return i
```

Sample route to generate user tokens: 
```python
@app.route('/get-token/<name>')
def get_token(name):
    """Sample view that returns jwt"""
    for i in user_storage:
        if i.name == name:
            return jsonify(login_manager.generate_jwt_token(i.identifier))  
    abort(401)
```

Sample route to load user:
```python
@app.route('/login/')
@login_manager.jwt_required
def login():
    """View that loads user from jwt present in request"""
    user = login_manager.load_user()
    return user.identifier
```

the example above shows the way of manual user loading but module also provides suitable proxy
The **jwt_required** decorator adds user loaded from request to **flask.g** and **current_user** loads it.  
```python
@app.route('/current_user_test/')
@login_manager.jwt_required
def test_current_user():
    return jwtl.current_user.identifier
```
flask.g lives inside application context (new for each request) so it's safe to store values in API there 
