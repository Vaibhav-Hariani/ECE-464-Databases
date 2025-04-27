from sqlalchemy.exc import IntegrityError
from sqlalchemy import select,delete
import secrets
from db_objects import *


Tables = {"student": (StudentData), "professor": (ProfessorData), "dean": {DeanData}}


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
            return ("Internal Error", -2)
    if uid < 0:
        return ("User already exists!", -1)
    try:
        login = Login(uname=args["uname"], password=args["pass"], type=type, uid=uid)
        with Session.begin() as session:
            session.add(login)
            create_session_token(login, session)
    except IntegrityError:
        return ("Invalid Username", -1)
    return (uid, 0)


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
            dean = DeanData(
                name=data["name"], email=data["email"], major_id=data["major_id"]
            )
            session.add(dean)
            session.commit()
            return dean.id
        except IntegrityError:
            return -1


##safety function
def create_professor(data: dict):
    with Session() as session:
        try:
            prof = DeanData(
                name=data["name"], email=data["email"], major_id=data["major_id"]
            )
            session.add(prof)
            session.commit()
            return prof.id
        except IntegrityError:
            return -1


def get_user(token_key: str):
    with Session() as session:
        token = get_token(token_key)
        login = session.merge(token).login
        extend_token(token)
        session.commit()
        table = Tables[login.type]
        stmt = select(table).where(login.uid == table.id)
        user = session.execute(stmt).fetchone()
        return user


def table_loader(
    Table_Label: str,
) -> list[StudentData] | list[ProfessorData] | list[DeanData]:
    with Session() as session:
        stmt = select("*").select_from(Tables[Table_Label])
        return session.execute(stmt).fetchall()


def create_gen_course(token_str: str, courseinfo: dict):
    token = get_token(token_str)
    if token.is_expired():
        return ("Token has Expired", -1)
    course_name = courseinfo["name"]
    course_code = courseinfo["course code"]
    try:
        with Session.begin() as session:
            token = get_token(token_str)
            login = session.merge(token).login
            if login.type != "dean":
                return ("You Should not have permission to access this resource!", -2)
            major_id = get_user(login).major_id
            with Session.begin() as session:
                course = CourseArchetype(
                    course_code=course_code, course_name=course_name, major_id=major_id
                )
                session.add(course)
    except IntegrityError:
        return ("Course Already Exists!", -1)
    return (course_code, 0)


def create_course_instance(courseinfo: dict, token_str: str):
    token = get_token(token_str)
    if token.is_expired():
        return ("Token has Expired", -1)
    course_code = courseinfo["course code"]
    get_course = select(CourseArchetype).where(
        CourseArchetype.course_code == course_code
    )
    try:
        with Session.begin() as session:
            token = get_token(token_str)
            login = session.merge(token).login
            if login.type != "dean" and login.type != "professor":
                return ("You Should not have permission to access this resource!", -2)
            arch = session.execute(get_course).fetchone()
            if arch is None:
                return ("Overarching Course No Longer exists", -2)
            arch = arch.CourseArchetype
            course = Course(
                prof_id=login.uid,
                course_id=arch.id,
                section=courseinfo["section"],
                semester_id=courseinfo["semester"].id,
                course_breakdown=courseinfo["breakdown"],
            )
            session.add(course)
    except IntegrityError:
        return ("Course Already Exists!", -1)
    return (course_code, 0)


##Get token from the token_str the user has
def get_token(token_str) -> SessionToken:
    stmt = select(SessionToken).where(SessionToken.token_key == token_str)
    with Session() as session:
        elements = session.execute(stmt).fetchone()
        if elements is None:
            return "Invalid Token"
        return elements.SessionToken


##This function is just for testing
def get_login(uid, type) -> Login:
    with Session() as session:
        stmt = select("*").where(Login.uid == uid).where(Login.type == type)
        element = session.execute(stmt).fetchone()
        return element


def create_session_token(login_obj: Login, session):
    token_key = secrets.token_bytes(64)
    creation_time = datetime.datetime.now(datetime.timezone.utc)
    expiration = creation_time + datetime.timedelta(hours=2)
    token = SessionToken(
        token_key=token_key,
        login=login_obj,
        uid=login_obj.id,
        expires_at=expiration,
    )
    session.add(token)
    return token_key


def extend_token(token: SessionToken):
    token.expires_at += datetime.timedelta(hours=2)


def login(uname, password) -> tuple[SessionToken, int]:
    udata = select(Login).where(Login.uname == uname, Login.password == password)
    # person = None
    key = -1
    with Session.begin() as session:
        first_el = session.execute(udata).fetchone()
        if first_el is None:
            return ("Username or Password is incorrect", -1)
        ##Should actually return a session token\
        login = first_el.Login
        key = login.token.token_key
        # token = login_obj.token
        if login.token.is_expired():
            session.delete(login.token)
            key = create_session_token(login, session)
    return (login.token, 0)


# def session_token_ass(uid):
#     if()
#     with Session() as session:
#         pass
