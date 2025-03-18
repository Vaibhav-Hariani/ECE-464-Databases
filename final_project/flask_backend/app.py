import os
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.sql import func

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
##This is very dependent on how the database is implemented
##Will switch to postgres for array support at a later date
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')
##Postgre: postgresql://username:password@host:port/database_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column()

