import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '75gA$8tQIWW67CZj04d7&Xj'

