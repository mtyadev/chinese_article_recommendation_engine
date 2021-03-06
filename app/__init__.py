from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv, find_dotenv
import os
from .extensions import db

app = Flask(__name__)

# Loading environment variables
load_dotenv(find_dotenv())
database_user = os.getenv("DB_USER")
database_password = os.getenv("DB_PASSWORD")
database_host = os.getenv("DB_HOST")
database_name = os.getenv("DB_NAME")

# Configuring and Intializing the Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}/{}'.format(database_user, database_password,
                                                                          database_host, database_name)

db.init_app(app)




from app import views

