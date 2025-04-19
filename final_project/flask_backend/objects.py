import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, MappedAsDataclass

##Todo: Change this name to something more descriptive
app = Flask(__name__)
##This is very dependent on how the database is implemented
##Will likely switch to postgres at a later date

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "database.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

##Postgre: postgresql://username:password@host:port/database_name


class Base(DeclarativeBase, MappedAsDataclass):
    pass


db = SQLAlchemy(app, model_class=Base)
##Structure is set to change


##Fundamental Login & User models
class StudentLogin(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    uname: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    student_id: Mapped[int]


class StudentData(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)


class ProfessorLogin(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    uname: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    prof_id: Mapped[int]


class ProfessorData(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)


class DeanLogin(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    uname: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    dean_id: Mapped[int]


class DeanData(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)


class CourseArchetype:
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


class StudentCourseLayer:
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int]
    course_id: Mapped[int]


class Assignment_Grade:
    id: Mapped[int] = mapped_column(primary_key=True)
    submitted: Mapped[bool]
    assignment_id: Mapped[int]
    SCL_id: Mapped[int]




if __name__ == "__main__":
    print(app.config["SQLALCHEMY_DATABASE_URI"])
    with app.app_context():
        ##Create all the models
        db.create_all()
