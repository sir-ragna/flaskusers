import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') 
    DATABASE = os.environ.get('DATABASE') or "database.db"