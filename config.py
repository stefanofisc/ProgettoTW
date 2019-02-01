import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dak/121ne12jn&aFGklA44891a'