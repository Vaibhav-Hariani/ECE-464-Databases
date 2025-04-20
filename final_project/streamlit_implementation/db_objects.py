import os
import datetime
from typing import List
from sqlalchemy import DateTime, create_engine, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    DeclarativeBase,
    MappedAsDataclass,
    Session,
    sessionmaker,
    relationship,
)

basedir = os.path.abspath(os.path.dirname(__file__))
DB_PATH = "sqlite:///" + os.path.join(basedir, "database.db")

engine = create_engine(DB_PATH, echo=False)
Session = sessionmaker(engine)
##Postgre: postgresql://username:password@host:port/database_name


class Base(DeclarativeBase):
    pass


##Fundamental Login & User models


class Login(Base):
    __tablename__ = "login"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uname: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    type: Mapped[str]
    uid: Mapped[int]
    token: Mapped[List["SessionToken"]] = relationship(
        "session_token", back_populates="Login", cascade="all, delete-orphan"
    )


class StudentData(Base):
    __tablename__ = "student_data"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)


class ProfessorData(Base):
    __tablename__ = "professor_data"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)


class DeanData(Base):
    __tablename__ = "dean_data"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    major_id: Mapped[int]


class CourseArchetype(Base):
    __tablename__ = "course_archetype"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_name: Mapped[str]
    course_code: Mapped[str]
    major_id: Mapped[int]


class Semesters(Base):
    __tablename__ = "semesters"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]


class Course(Base):
    __tablename__ = "course"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    running: Mapped[bool]
    prof_id: Mapped[int]
    course_id: Mapped[int]
    section_id: Mapped[int]
    semester_id: Mapped[int]
    course_breakdown: Mapped[str]


class Assignment(Base):
    __tablename__ = "assignment"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int]
    assignment_weight: Mapped[int]
    due_date: Mapped[datetime.datetime]
    name: Mapped[str]


class StudentCourseLayer(Base):
    __tablename__ = "student_course_layer"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int]
    course_id: Mapped[int]


class AssignmentGrade(Base):
    __tablename__ = "assignment_grade"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    submitted: Mapped[bool]
    time_submitted: Mapped[datetime.datetime]
    assignment_id: Mapped[int]
    student_course_layer_id: Mapped[int]


class SessionToken(Base):
    __tablename__ = "session_token"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    active: Mapped[bool] = mapped_column(default=True)
    uid: Mapped[int] = mapped_column(ForeignKey("Login.id"))
    login_obj: Mapped[Login] = relationship("Login", back_populates="session_token")
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))

    def is_expired(self) -> bool:
        """Checks if the token has expired."""
        return datetime.datetime.now(datetime.timezone.utc) > self.expires_at



Base.metadata.create_all(engine)
if __name__ == "__main__":
    pass
    # with Session(engine) as session:
    #     pass

    # print(app.config["SQLALCHEMY_DATABASE_URI"])
    # with app.app_context():
    #     ##Create all the models
    #     db.create_all()
