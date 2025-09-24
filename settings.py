import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        default='sqlite:///db.sqlite3'
    )
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', default='secret-string')
