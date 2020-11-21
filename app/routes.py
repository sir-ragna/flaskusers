from app import app
from app.database import *
from flask import render_template, request, flash, redirect, url_for, session
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            if is_valid_user_id(session['user_id']):
                return f(*args, **kwargs) # We found a valid user
        app.logger.warning("No session, this pages requires login")
        flash("This pages requires you to sign-in")
        return redirect(url_for('login'))    
    return decorated_function

@app.route('/')
def homepage():
    user = None
    if 'user_id' in session:
        user_id = session['user_id']
        user = get_user(user_id)
    
    return render_template('home.html.j2', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.clear()
        if 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']
            if check_password(email, password):
                flash("Authentication succeeded")
                user_id = get_user_id(email)
                session['user_id'] = user_id
                return redirect(url_for('homepage'))
            else:
                flash("Failed to authenticate")
        
    return render_template('login.html.j2')

@app.route('/logout')
def logout():
    session.clear()
    flash("signed out")
    return redirect(url_for('homepage'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']
            try:
                create_user(email, password)
                flash(f"User '{email}' created")
                return redirect(url_for('homepage'))
            except Exception as ex:
                app.logger.error('Could not register: {}'.format(ex), exc_info=True)
                flash("Failed to register")
       
    return render_template('register.html.j2')

@app.route('/admin')
@login_required
def admin():
    return "Only signed in users can see this"

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user_id = session['user_id']

    if request.method == 'POST':
        if 'nickname' in request.form:
            save_nickname(user_id, request.form['nickname'])
        elif 'verifyme' in request.form:
            generate_verification_link(user_id)
            # TODO sent email somehow

    user = get_user(user_id)
    return render_template('profile.html.j2', user=user)

@app.route('/activate/<string:activation_code>')
def activate_email(activation_code):
    try:
        if verify_user_email(activation_code):
            flash("User has been activated")
            return redirect(url_for("homepage"))
    except Exception as ex:
        print("{}".format(ex))
    
    flash("Could not activate user")
    return redirect(url_for("homepage"))
    