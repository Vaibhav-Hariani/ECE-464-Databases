from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
import secrets
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
            return ("-1", -2)
    if uid < 0:
        return ("User already exists!",-1)
    try:
        login = Login(uname=args["uname"], password=args["pass"], type=type, uid=uid)
        with Session.begin() as session:
            session.add(login)
            create_session_token(login,session)
    except IntegrityError:
        return ("Invalid Username",1)
    return (uid,0)


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
def get_login(uid,type) -> Login:
    with Session() as session:
        stmt = select('*').where(Login.uid == uid).where(Login.type == type)
        element = session.execute(stmt).fetchone()
        return element

def create_session_token(login_obj: Login,session):
    token_key= secrets.token_bytes(64)
    creation_time = datetime.datetime.now(datetime.timezone.utc) 
    expiration = creation_time + datetime.timedelta(hours=2)
    token = SessionToken(token_key=token_key, uid=Login.id, expires_at=expiration)
    session.add(token)
    login_obj.token = token
    return token_key

def extend_token(token: SessionToken):
    token.expires_at += datetime.timedelta(hours=2)

def login(uname,password):
    udata = select(Login).where(
        Login.uname == uname, Login.password == password
    )
    # person = None
    with Session() as session:
        first_el = session.execute(udata).fetchone()
        if first_el is None:
            return ("Username or Password is incorrect", -1)
        ##Should actually return a session token\
        login = first_el.Login

        # token = login_obj.token
        if (not login.token.active) or login.token.is_expired():
            create_session_token(login,session)
            session.commit()
        return (login.token, 0)
    
# def session_token_ass(uid):
#     if()
#     with Session() as session:
#         pass
