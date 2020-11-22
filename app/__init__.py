from flask import Flask
from config import Config
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(Config)
mail = Mail(app)

if app.config['MAIL_SERVER'] == None:
    app.logger.error("No MAIL_SERVER defined")

if app.config['MAIL_PORT'] == None:
    app.logger.error("No MAIL_PORT defined")

if app.config['MAIL_USERNAME'] == None:
    app.logger.error("No MAIL_USERNAME defined")

if app.config['MAIL_PASSWORD'] == None:
    app.logger.error("No MAIL_PASSWORD defined")

from app import routes
from app import database
from app import cli