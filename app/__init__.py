from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['MONGO_DBNAME'] = 'stefanodb'
app.config['MONGO_URI'] = 'mongodb://stefano:Cisterna94@ds153974.mlab.com:53974/stefanodb'

from app import routes