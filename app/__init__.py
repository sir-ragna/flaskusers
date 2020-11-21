from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

from app import routes
from app import database
from app import cli