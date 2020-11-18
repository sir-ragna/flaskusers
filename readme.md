
# Flask project to create the most basic login possible

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

```python
# file: application.py
from app import app
```

```python
# file: app/__init__.py
import flask import Flask

app = Flask(__init__)

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

### Create a run script

```sh
#!/bin/sh
# file: run.sh

source venv/bin/activate
flask run
```

Now we can easily start our project by executing `./run.sh`.

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

```SQL
CREATE TABLE "users" (
	"user_id"	INTEGER,
	"user_name"	TEXT UNIQUE,
	"user_hash"	TEXT,
	PRIMARY KEY("user_id" AUTOINCREMENT)
);
```

I use the bcrypt module for hashing. So we need to install it.

```sh
pip install bcrypt
```

