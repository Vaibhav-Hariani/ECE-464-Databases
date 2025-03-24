import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
##This is very dependent on how the database is implemented
##Will switch to postgres for array support at a later date
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "database.db"
)
##Postgre: postgresql://username:password@host:port/database_name
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(app, model_class=Base)
##Structure is set to change


##Fundamental Login & User models
class Student_Login(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    uname: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    student_id: Mapped[int]


class Student_Data(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)


class Professor_Login(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    #     name: Mapped[str]
    uname: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    prof_id: Mapped[int]


class Professor_Data(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)


class Dean_Login(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    #     name: Mapped[str]
    uname: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    dean_id: Mapped[int]


class Dean_Data(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)


class Course_Archetype:
    id: Mapped[int] = mapped_column(primary_key=True)
    course_name: Mapped[str]
    course_code: Mapped[str]
    major_id: Mapped[int]


class Semesters:
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class Course:
    id: Mapped[int] = mapped_column(primary_key=True)
    Running: Mapped[bool]
    prof_id: Mapped[int]
    course_id: Mapped[int]
    section_id: Mapped[int]
    semester_id: Mapped[int]
    course_breakdown: Mapped[str]


class Assignment:
    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int]
    assignment_weight: Mapped[int]
    Name: Mapped[str]


class Student_Course_Layer:
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int]
    course_id: Mapped[int]


class Assignment_Grade:
    id: Mapped[int] = mapped_column(primary_key=True)
    submitted: Mapped[bool]
    assignment_id: Mapped[int]
    SCL_id: Mapped[int]


if __name__ == "__main__":
    with app.app_context():
        ##Create all the models
        db.create_all()
