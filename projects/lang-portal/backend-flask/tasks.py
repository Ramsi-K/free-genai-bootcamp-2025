from invoke import task
from lib.db import db

@task
def init_db(c):
  from flask import Flask
  app = Flask(__name__)
  db.init(app)
  print("Database initialized successfully.")