import os
import datetime
from typing import List, Optional
from sqlalchemy import (
    Column,
    DateTime,
    event,
    String,
    Table,
    UniqueConstraint,
    create_engine,
    ForeignKey,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    DeclarativeBase,
    sessionmaker,
    relationship,
)
from sqlalchemy.engine import URL

# basedir = os.path.abspath(os.path.dirname(__file__))
# For Sqllite: Unsupported for some funcs or blobs.
# DB_PATH = "sqlite:///" + os.path.join(basedir, "database.db")
## For SqlAlchemypi

url = URL.create(
    drivername="postgresql",
    username="postgres",
    password="password",
    host="localhost",
    port="5432",
    database="postgres",
)

engine = create_engine(url, echo=False)
Session = sessionmaker(engine, expire_on_commit=False)
# Postgre: postgresql://username:password@host:port/database_name


class Base(DeclarativeBase):
    pass


class ExpiredToken(Exception):
    pass


##Association table for bi-directional many to many
##Used for student to course relationship
student_course_assoc = Table(
    "student_course_assoc_table",
    Base.metadata,
    Column("left_id", ForeignKey("courses.id"), primary_key=True),
    Column("right_id", ForeignKey("student_data.id"), primary_key=True),
)


##Fundamental Login & User models
class Login(Base):
    __tablename__ = "login"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uname: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    type: Mapped[str]
    uid: Mapped[int]
    token: Mapped["SessionToken"] = relationship(back_populates="login")

    def __repr__(self):
        return self.uname


class StudentData(Base):
    __tablename__ = "student_data"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    reg_courses: Mapped[List["Courses"]] = relationship(
        secondary=student_course_assoc, back_populates="students"
    )
    submissions: Mapped[List["AssignmentGrade"]] = relationship(
        back_populates="student"
    )

    def __repr__(self):
        return self.name


class ProfessorData(Base):
    __tablename__ = "professor_data"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    major_id: Mapped[int]
    courses: Mapped[List["Courses"]] = relationship(back_populates="prof")

    def __str__(self):
        return f"{self.name}"


class DeanData(Base):
    __tablename__ = "dean_data"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    major_id: Mapped[int]

    def __str__(self):
        return f"{self.name}"


##Simple human-readable table
class Major_Labels(Base):
    __tablename__ = "major"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]

    def __str__(self):
        return f"{self.name}"


class CourseArchetype(Base):
    __tablename__ = "course_archetypes"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_name: Mapped[str] = mapped_column()
    course_code: Mapped[str] = mapped_column(unique=True)
    courses: Mapped[set["Courses"]] = relationship(back_populates="archetype")
    major_id: Mapped[int]

    def __str__(self):
        return f"{self.course_name}"


class Semesters(Base):
    __tablename__ = "semesters"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)

    def __str__(self):
        return self.name


class Courses(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    running: Mapped[bool] = mapped_column(default=True)
    prof: Mapped["ProfessorData"] = relationship(back_populates="courses")
    prof_id: Mapped[int] = mapped_column(ForeignKey("professor_data.id"))
    archetype: Mapped["CourseArchetype"] = relationship(back_populates="courses")
    course_id: Mapped[int] = mapped_column(ForeignKey("course_archetypes.id"))
    section: Mapped[str]
    semester_id: Mapped[int]
    course_breakdown: Mapped[List["AssignSpec"]] = relationship(back_populates="course")
    curve: Mapped[Optional[str]]
    students: Mapped[set["StudentData"]] = relationship(
        secondary=student_course_assoc, back_populates="reg_courses"
    )

    __table_args__ = (
        UniqueConstraint(
            "course_id", "semester_id", "section", name="uq_course_sem_section"
        ),
        # 2. Index for faster lookup (Goal 1) - queries filtering by course AND semester
        # Index('ix_course_semester', 'course_id', 'semester_id'),
    )

    def __str__(self):
        with Session() as session:
            course_code = session.merge(self).archetype.course_code
            sem_name = session.get(Semesters, self.semester_id).name
            return f"{course_code}, Section {self.section} in {sem_name}"


##General classes for all assignments
class AssignSpec(Base):
    __tablename__ = "assign_type"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course: Mapped["Courses"] = relationship(back_populates="course_breakdown")
    label: Mapped[str] = mapped_column(unique=True)
    weight: Mapped[float]
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"))
    assignments: Mapped[List["Assignment"]] = relationship(back_populates="type")

    def __str__(self):
        return f"{self.label}"


class Assignment(Base):
    __tablename__ = "assignment"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped["AssignSpec"] = relationship(back_populates="assignments")
    spec_id: Mapped[int] = mapped_column(ForeignKey("assign_type.id"))
    submissions: Mapped[List["AssignmentGrade"]] = relationship(
        back_populates="assignment"
    )
    weight: Mapped[float]
    due_date: Mapped[datetime.datetime]
    name: Mapped[str]
    curve: Mapped[Optional[str]]
    __table_args__ = (
        UniqueConstraint("spec_id", "name", name="uq_spec_name"),
        # 2. Index for faster lookup (Goal 1) - queries filtering by course AND semester
        # Index('ix_course_semester', 'course_id', 'semester_id'),
    )

    def __str__(self):
        return f"{self.name}"


class AssignmentGrade(Base):
    __tablename__ = "assignment_grade"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    assignment: Mapped["Assignment"] = relationship(back_populates="submissions")
    assign_id: Mapped[int] = mapped_column(ForeignKey("assignment.id"))
    grade: Mapped[float] = mapped_column(default=0.0)
    submitted: Mapped[bool] = mapped_column(default=False)
    time_submitted: Mapped[Optional[datetime.datetime]]
    student_id = mapped_column(ForeignKey("student_data.id"))
    student: Mapped["StudentData"] = relationship(back_populates="submissions")
    curved_score: Mapped[int] = mapped_column(default=0.0)
    __table_args__ = (
        UniqueConstraint("student_id", "assign_id", name="uq_submissions"),
        # 2. Index for faster lookup (Goal 1) - queries filtering by course AND semester
        # Index('ix_course_semester', 'course_id', 'semester_id'),
    )


def set_session_time():
    return datetime.datetime.now() + datetime.timedelta(hours=2)


class SessionToken(Base):
    __tablename__ = "session_token"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    token_key: Mapped[str] = mapped_column(String(32))
    active: Mapped[bool] = mapped_column(default=True)
    login: Mapped["Login"] = relationship("Login", back_populates="token")
    uid: Mapped[int] = mapped_column(ForeignKey("login.id"))
    expires_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=set_session_time()
    )

    def is_expired(self) -> bool:
        """Checks if the token has expired."""
        return self.active and datetime.datetime.now() > self.expires_at


Base.metadata.create_all(engine)
if __name__ == "__main__":
    pass
