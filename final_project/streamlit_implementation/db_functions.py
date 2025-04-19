from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from final_project.streamlit_implementation.db_objects import *


Tables = {"Student": (StudentData), "Professor": (ProfessorData), "Dean": {DeanData}}


# @app.route("/create_user", methods=['POST'])
def create_user(args):
    error = None
    uid = None
    ##Need to implement a security layer to guarantee
    # this is a valid request.
    type = args["obj_class"]
    match type:
        case "student":
            uid = create_student(args)
        case "dean":
            uid = create_dean(args)
        case "professor":
            uid = create_professor(args)
        case _:
            return (-1, 400)
    if uid < 0:
        return ("Data Already Exists!", 405)
    login = Login(args["uname"], args["pass"], type, uid)
    with Session.begin() as session:
        session.add(login)
    return uid


def create_student(data: dict):
    with Session.begin() as session:
        try:
            student = StudentData(name=data["name"], email=data["email"])
            session.add(student)
            return student.id
        except IntegrityError:
            return -1


def create_dean(data: dict):
    with Session.begin() as session:
        try:
            dean = DeanData(data["name"], data["email"], data["major_id"])
            session.add(dean)
            return dean.id
        except IntegrityError:
            return -1


##safety function
def create_professor(data: dict):
    with Session.begin() as session:
        try:
            prof = ProfessorData(data["name"], data["email"], data["major_id"])
            session.add(prof)
            return prof.id
        except IntegrityError:
            return -1


def login(args):
    udata = select(Login).where(
        Login.uname == args["uname"] and Login.password == args["password"]
    )
    if len(login <= 1):
        return ("Username or Password is incorrect", 405)
    user = udata[0]
    print(user)
