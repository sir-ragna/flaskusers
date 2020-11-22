import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') 
    DATABASE = os.environ.get('DATABASE') or "database.db"
    PASSWORD = os.environ.get('PASSWORD')

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')