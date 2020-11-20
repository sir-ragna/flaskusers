
# Flask project to create the most basic login possible

### If you are only interested in running the source code

```bash
git clone https://github.com/sir-ragna/flaskusers
cd flaskusers
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run
```

If not.

# Creating and activating the virtual environment

Create a virtual environment and activate it.

```bash
python -m venv venv
source venv/bin/activate
```

For windows the activation is by executing `& ./venv/Scripts/activate.ps1`

Once the virtual environment has been activated you can install flask and other required modules.

```
(venv) [user@hostname flasklogin]$ pip install flask
```

## Create the basic files and folder layout

Create a file `application.py`.

```python
# file: application.py
from app import app
```

Create an `app` directory with an `__init__.py`.

```python
# file: app/__init__.py
from flask import Flask

app = Flask(__name__)

from app import routes
from app import database
```

Inside the app directory I also create a `routes.py` and a `database.py` file.

### Creating our first route.

Inside the routes.py file we create our first route.

```python
# file: app/routes.py
from app import app

@app.route('/')
def homepage():
    return "Hello world!"
```

We test it by executing `flask run`. (Do not forget to make sure that your environment is activated first.)

```
(venv) [user@hostname flasklogin]$ flask run
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
127.0.0.1 - - [18/Nov/2020 16:45:51] "GET / HTTP/1.1" 200 -
```

### Create a run script (for linux)

```sh
#!/bin/sh
# file: run.sh

source venv/bin/activate
flask run
```

Now we can easily start our project by executing `./run.sh`.

### Creat a run script (for windows)

```pwsh
# file: run.ps1
& .\venv\Scripts\activate.ps1
flask run
```

Now you can run your project by executing `& .\run.ps1`.

### Running the server in debug mode

Usually during development we'll want to run our server in debug mode.
To do this we first install `python-dotenv` and create a `.flaskenv` file.

```sh
pip install python-dotenv
```

The `.flaskenv` file:

```sh
# file: .flaskenv
FLASK_ENV=development
FLASK_DEBUG=1
```

## Jinja2 Templates

Create a directory `app/templates/`. Here we'll place our jinja2 templates.

Lets start with a `app/templates/base.html.j2` file.

```jinja2
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>app</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>

{% block content %}
{% endblock content %}

</body>
</html>
```

We create another file `app/templates/login.html.j2`

```jinja2
{% extends "base.html.j2" %}

{% block content %}
<form method="post" action="{{ url_for('login') }}">
    <label for="username">username</label> 
    <input name="username" id="username" type="text"> 
    <br>
    <br>
    <label for="password">password</label>
    <input name="password" id="password" type="password">
    <br>
    <button type="submit">sign in</button>
</form>
{% endblock content %}

```

### render the templates

We add another route to our routes.py file.

```python
# added to routes.py

@app.route('/login')
def login():
    return render_template('login.html.j2')
```

You should now see the username and password field getting rendered when browsing to `http://localhost:5000/login`.

## Capturing the POST values

We modify the routes.py file to allow POST requests and we verify that we receive the `username` and `password` values.

```python
from app import app
from flask import render_template, request

@app.route('/')
def homepage():
    return "Hello world!"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            print(username, ':', password)
        
    return render_template('login.html.j2')
```

## Creating users and authentication

First we need to create table to contain our users.

```python
# file: app/database.py
import sqlite3
# Create the database tables in case that they do not exist yet.
db_schema_script = """
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "users" (
	"user_id"	INTEGER,
	"user_name"	TEXT UNIQUE,
	"user_hash"	TEXT,
	PRIMARY KEY("user_id" AUTOINCREMENT)
);
COMMIT;
"""
with sqlite3.connect(DATABASE) as conn:
    cursor = conn.cursor()
    cursor.executescript(db_schema_script)
    conn.commit()
    print("Executed DB schema script")
    cursor.close()
```

I use the bcrypt module for hashing. So we need to install it.

```sh
pip install bcrypt
```

Again, do not forget that you should do this in the activated `(env)`.

We add a few database functions.

```python
import sqlite3
import bcrypt
from app import app

DATABASE = app.config['DATABASE']

def hash_password(password):
    """Hashes an utf-8 string and returns an utf-8 string of the hash"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')

def create_user(username, password):
    """Creates a new user"""
    with sqlite3.connect(DATABASE) as conn:
        pw_hash = hash_password(password)
        conn.execute("INSERT INTO users (user_name, user_hash) VALUES (?, ?)", (username, pw_hash))
        conn.commit()

def check_password(username, password):
    """Return True upon success, False upon failure"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT user_id, user_name, user_hash FROM users WHERE user_name = ?;", (username,))
        user_id, user_name, user_hash = cursor.fetchone()
        return bcrypt.checkpw(password.encode('utf-8'), user_hash.encode('utf-8'))

def get_user_id(username):
    """Return the user_id for a given username"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT user_id FROM users WHERE user_name = ?;", (username,))
        user_id = cursor.fetchone()[0]
        return user_id

def is_valid_user_id(user_id):
    """Returns True if the user_id exists, False if not"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT user_id FROM users WHERE user_id = ?;", (user_id,))    
        return cursor.fetchone()[0] != None

# Create the database tables in case that they do not exist yet.
db_schema_script = """
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "users" (
	"user_id"	INTEGER,
	"user_name"	TEXT UNIQUE,
	"user_hash"	TEXT,
	PRIMARY KEY("user_id" AUTOINCREMENT)
);
COMMIT;
"""
with sqlite3.connect(DATABASE) as conn:
    cursor = conn.cursor()
    cursor.executescript(db_schema_script)
    conn.commit()
    print("Executed DB schema script")
    cursor.close()
```

## Register a new user

Here is the full workflow for registering a new user.
First, we have a basic page.

```jinj2
{% extends "base.html.j2" %}

{% block content %}
<h1>Register an account</h1>
<form method="post" action="{{ url_for('register') }}">
    <label for="username">username</label> 
    <input name="username" id="username" type="text"> 
    <br>
    <br>
    <label for="password">password</label>
    <input name="password" id="password" type="password">
    <br>
    <button type="submit">sign up</button>
</form>
<br><br>
<a href="{{ url_for('homepage') }}">return to homepage</a>
{% endblock content %}
```

Things to note are the input. The NAME attributes will determine which
data is going to get passed through the HTTP request.

- `<input name="username">`
- `<input name="password">`

The METHOD attribute of the `<form>` is going to decide how the information is sent.

- `<form method="post">`

To render this template and to deal with the data. Write the following function.

```python
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            try:
                create_user(username, password)
                flash(f"User '{username}' created")
                return redirect(url_for('homepage'))
            except Exception as ex:
                app.logger.error('Could not register: {}'.format(ex), exc_info=True)
                flash("Failed to register")
       
    return render_template('register.html.j2')
```

1. we check whether the method is a post.
1.1 If it happens to be a GET request we can simply render the page
2. We whether the 'username' and 'password' values are present
3. We `try:`  to execute `create_user(username, password)`

The reason for using a `try:` here is because in the create_user function there is no error handeling.

```python
def create_user(username, password):
    """Creates a new user"""
    with sqlite3.connect(DATABASE) as conn:
        pw_hash = hash_password(password)
        conn.execute("INSERT INTO users (user_name, user_hash) VALUES (?, ?)", (username, pw_hash))
        conn.commit()
```

If we try to INSERT a duplicate username value the `conn.commit()` line will raise
an exception. This exception will be catched in the `register()` function on the line
`except Exception as ex:`.

The reason for this is because we put the column in our sqlite database on `unique`.

```
"user_name"	TEXT UNIQUE
```

Without the UNIQUE attribute on this column name it would be possible to create 
multiple users with the same name.


