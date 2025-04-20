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
            return (-1, -2)
    if uid < 0:
        return ("User already exists!",-1)
    try:
        login = Login(uname=args["uname"], password=args["pass"], type=type, uid=uid)
    except IntegrityError:
        return ("Invalid Username",1)
    with Session.begin() as session:
        session.add(login)
    return (uid,1)


def create_student(data: dict):
    id = 0
    with Session() as session:
        try:
            student = StudentData(name=data["name"], email=data["email"])
            session.add(student)
            session.commit()
            return student.id
        except IntegrityError:
            return -1



def create_dean(data: dict):
    with Session() as session:
        try:
            dean = DeanData(data["name"], data["email"], data["major_id"])
            session.add(dean)
            session.commit()
            return dean.id
        except IntegrityError:
            return -1


##safety function
def create_professor(data: dict):
    with Session() as session:
        try:
            prof = ProfessorData(name=data["name"], email=data["email"])
            session.add(prof)
            session.commit()
            return prof.id
        except IntegrityError:
            return -1

def table_loader(Table_Label: str) -> list[StudentData] | list [ProfessorData] | list [DeanData]:
    with Session() as session:
        stmt = select('*').select_from(Tables[Table_Label])
        return session.execute(stmt).fetchall()


##This function is just for testing
def get_login(uid) -> Login:
    with Session() as session:
        stmt = select('*').where(Login.uid == uid)
        element = session.execute(stmt).fetchone()
        return element


def login(uname,password):
    udata = select(Login.uid).where(
        Login.uname == uname, Login.password == password
    )
    person = None
    with Session() as session:
        id = session.execute(udata).fetchone()
        if id is None:
            return ("Username or Password is incorrect", -1)
        ##Should actually return a session token
        return (id, 0)
    
def session_token_ass(uid):
    if()
    with Session() as session:
        pass
