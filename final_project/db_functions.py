from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, delete
import secrets
from db_objects import *
from fourFn import parse
from typing import TypeVar

##For analyzing return types:
#  1 - Repeat Data: Returned original element instead
# 0 - Success
# -1 - Failure,
# -2 - Permissions Failure

##Helpers for testing
Tables = {"student": (StudentData), "professor": (ProfessorData), "dean": {DeanData}}

T = TypeVar("T")  # the variable name must coincide with the string


def table_loader(obj: type[T]) -> list[T]:
    with Session() as session:
        return session.query(obj).all()


def get_obj_from_id(id, obj_type: type[T]) -> T:
    with Session() as session:
        return session.get(obj_type, id)


##User creation
def create_user(args) -> tuple[int | str, int]:
    error = None
    uid = None
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


def create_student(data: dict) -> StudentData | int:
    id = 0
    with Session() as session:
        try:
            student = StudentData(name=data["name"], email=data["email"])
            session.add(student)
            session.commit()
            return student.id
        except IntegrityError:
            return -1


def create_dean(data: dict) -> DeanData | int:
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
def create_professor(data: dict) -> ProfessorData | int:
    with Session() as session:
        try:
            prof = ProfessorData(
                name=data["name"], email=data["email"], major_id=data["major_id"]
            )
            session.add(prof)
            session.commit()
            return prof.id
        except IntegrityError:
            return -1


def create_major(major_name) -> Major_Labels:
    with Session() as session:
        major_obj = Major_Labels(name=major_name)
        session.add(major_obj)
        session.commit()
        return major_obj.id


##1 means the object already exists, so creation failed
## As protection, that existing object is returned
def create_semester(semester_name) -> tuple[Semesters, int]:
    try:
        with Session() as session:
            sem = Semesters(name=semester_name)
            session.add(sem)
            session.commit()
            return (sem.id, 0)
    except IntegrityError:
        with Session() as session:
            stmt = select(Semesters).where(semester_name == semester_name)
            ret = session.execute(stmt).scalar()
            return (ret.id, 1)


def get_semester(semester_id) -> tuple[List[Semesters], int]:
    with Session() as session:
        stmt = select(Semesters).where(Semesters.id == semester_id)
        return (session.execute(stmt).fetchall(), 0)


##Course Creation
def create_gen_course(key: str, courseinfo: dict) -> tuple[Courses, int]:
    user, utype = get_user(key)
    course_name = courseinfo["name"]
    course_code = courseinfo["course_code"]
    with Session() as session:
        try:
            user, utype = get_user(key)
            if utype != "dean" and utype != "professor":
                return ("You Should not have permission to access this resource!", -2)
            major_id = user.major_id
            course = CourseArchetype(
                course_code=course_code, course_name=course_name, major_id=major_id
            )
            session.add(course)
            session.commit()
            return (course.id, 0)
        except IntegrityError:
            session.rollback()
            stmt = select(CourseArchetype).where(course_code == course_code)
            ret = session.execute(stmt).scalar()
            return (ret, 1)


def get_course(courseinfo: dict) -> Courses:
    get_arch = select(CourseArchetype.id).where(
        CourseArchetype.course_code == courseinfo["course_code"]
    )
    with Session() as session:
        arch_id = session.execute(get_arch).scalar_one()
        stmt = select(Courses).where(
            Courses.semester_id == courseinfo["semester id"],
            Courses.course_id == arch_id,
            Courses.section == courseinfo["section"],
        )
        return session.execute(stmt).scalar_one()


def create_course_instance(courseinfo: dict, key: str) -> tuple[Courses, int]:
    course_code = courseinfo["course_code"]
    get_arch = select(CourseArchetype).where(CourseArchetype.course_code == course_code)
    try:
        with Session.begin() as session:
            user, utype = get_user(key)
            if utype != "professor":
                return ("You Should not have permission to access this resource!", -2)
            arch = session.execute(get_arch).fetchone()
            if arch is None:
                return ("Overarching Course No Longer exists", -2)
            arch = arch[0]
            course = Courses(
                prof_id=user.id,
                archetype=arch,
                section=courseinfo["section"],
                semester_id=courseinfo["semester id"],
            )
            session.add(course)
            return (course, 0)
    except IntegrityError:
        return get_course(courseinfo), 1


##Assignment Lifecycle
def create_breakdown(
    course_id: int, assign_spec: List[tuple[str, float]]
) -> tuple[str, int]:
    status = 0
    for assign_type, weight in assign_spec:
        type, status = add_gen_assign(assign_type, weight, course_id)
        if status != 0:
            print(f"Failed to Create {assign_type}, already exists")
    return ("Success!", status)


def add_gen_assign(
    assign_type: str, weight: float, course_id: int
) -> tuple[AssignSpec | str, int]:
    try:
        with Session() as session:
            course = session.get(Courses, course_id)
            new_arch = AssignSpec(course=course, weight=weight, label=assign_type)
            session.add(new_arch)
            session.commit()
            return (new_arch, 0)
    except IntegrityError:
        return ("Assignment type already exists", 1)


##Creates empty AssignmentGrades for each student
def create_grades(assign: Assignment) -> List[AssignmentGrade]:
    try:
        with Session.begin() as session:
            assign = session.merge(assign)
            students = assign.type.course.students
            for student in students:
                submittable = AssignmentGrade(assignment=assign, student=student)
                session.add(submittable)
        return ("Success!", 0)
    except IntegrityError:
        return ("Failed: Student already has submittable", -1)


def new_assignment(course_id, assign_type: str, args: dict) -> tuple[Assignment, int]:
    try:
        with Session.begin() as session:
            spec_stmt = select(AssignSpec).where(
                AssignSpec.label == assign_type, AssignSpec.course_id == course_id
            )
            spec = session.execute(spec_stmt).scalar_one_or_none()
            if spec is None:
                return "Invalid Label", -1
            assign = Assignment(
                type=spec,
                weight=args["weight"],
                due_date=args["due_date"],
                name=args["name"],
            )
            session.add(assign)
        return (assign, 0)
    except IntegrityError:
        with Session() as session:
            spec_stmt = select(AssignSpec.id).where(
                AssignSpec.label == assign_type, AssignSpec.course_id == course_id
            )
            spec_id = session.execute(spec_stmt).scalar_one_or_none()
            get_assign = select(Assignment).where(
                Assignment.name == args["name"], Assignment.spec_id == spec_id
            )
            return (session.execute(get_assign).scalar_one_or_none(), 1)


def assign_curve(obj: Courses| Assignment, curve_str) -> int:
    with Session.begin() as session:
        obj = session.merge(obj)
        obj.curve = curve_str
        session.commit()
        return 0

##Depending on future work, may need to add ability to upload
def submit(token: str, assignment: Assignment) -> tuple[String, int]:
    user, utype = get_user(token)
    if utype != "student":
        return ("Not a Student", -2)
    with Session.begin() as session:
        stmt = select(AssignmentGrade).where(
            AssignmentGrade.student_id == user.id,
            AssignmentGrade.assign_id == assignment.id,
        )
        gradable = session.execute(stmt).scalar()
        gradable.submitted = True
        gradable.time_submitted = get_time()
    return ("Success!", 0)


def grade(key: str, submission: AssignmentGrade, grade) -> tuple[AssignmentGrade, int]:
    user, utype = get_user(key)
    if utype != "professor":
        return ("Not a Professor", -2)
    with Session() as session:
        submission = session.merge(submission)
        submission.submitted = True
        submission.grade = grade
        session.commit()
        return (submission, 0)
##Returns all assignment specs
def get_assign_specs(course: Courses):
    with Session() as session:
        course = session.merge(course)
        return course.course_breakdown


def get_assignments(assigns: AssignSpec):
    with Session() as session:
        assigns = session.merge(assigns)
        return assigns.assignments

def get_grades(course: Courses):
    with Session() as session:
        course = session.merge(course)
        students = course.students
        curved_grades = [get_student_grade(None,course,student.id)[0]
                   for student in students]
        curved_grades.sort()
        raw_grades = [get_raw_scores(course, student.id)[0] for student in students]
        raw_grades.sort()
        return curved_grades, raw_grades
    
def get_raw_scores(course: Courses, uid):
    with Session() as session:
        breakdown = session.merge(course).course_breakdown
        grade = 0.0
        for spec in breakdown:
            weight = spec.weight
            assignments = spec.assignments
            lgrade = 0
            for assign in assignments:
                curve = assign.curve
                lweight = assign.weight
                stmt = select(AssignmentGrade.grade).where(
                    AssignmentGrade.student_id==uid, AssignmentGrade.assign_id==assign.id
                )
                ##Assumption is that each student only submits one grade per assignment
                assign_grade = session.execute(stmt).scalar()
                lgrade += assign_grade * lweight
            grade += weight * lgrade
        return (grade, 0)


def get_student_grade(key: str|None, course: Courses, uid=None) -> tuple[float| str, int] :
    uid = uid
    utype = "student"
    if uid is None:
        user, utype = get_user(key)
        uid = user.id
    if utype !="student":
        return ("Invalid User", 0)
    with Session() as session:
        breakdown = session.merge(course).course_breakdown
        grade = 0.0
        for spec in breakdown:
            weight = spec.weight
            assignments = spec.assignments
            lgrade = 0
            for assign in assignments:
                curve = assign.curve
                lweight = assign.weight
                stmt = select(AssignmentGrade.grade).where(
                    AssignmentGrade.student_id==uid, AssignmentGrade.assign_id==assign.id
                )
                ##Assumption is that each student only submits one grade per assignment
                assign_grade = session.execute(stmt).scalar()
                lgrade += apply_curve(curve, assign_grade, assign) * lweight
            grade += weight * lgrade
        grade = apply_curve(course.curve, grade)
        return (grade, 0)


##Grades are stored in 0-100 format.
##This needs to take those values, and curve them according to
def apply_curve(curve, raw, data=None):
    if curve is None:
        return raw
    return parse(curve, raw,data)


def get_time():
    return datetime.datetime.now()


##Course management
def get_prof_courses(
    key: str,
) -> tuple[List[Courses], List[CourseArchetype], List[Semesters], int]:
    user, utype = get_user(key)
    with Session() as session:
        user = session.merge(user)
        if(utype != "professor"):
            return ("Invalid UserType")
        courses = user.courses
        archetypes = []
        semesters = []
        for course in courses:
            semesters.extend(get_semester(course.semester_id)[0])
            archetypes.append(course.archetype)
        return (courses, archetypes, semesters, 0)


def reg_student(key: str, course_data: dict | None = None, course_id=None):
    student = get_user(key)[0]
    with Session.begin() as session:
        student = session.merge(student)
        if course_id is None:
            course = get_course(course_data)
            course.students.add(student)
        else:
            course = session.get(Courses, course_id)
            course.students.add(student)
    return ("Success", 0)


##Token And Login Behavior/retrieval
def login(uname, password) -> tuple[SessionToken, int]:
    udata = select(Login).where(Login.uname == uname, Login.password == password)
    # person = None
    key = -1
    with Session.begin() as session:
        login = session.execute(udata).scalar_one_or_none()
        if login is None:
            return ("Username or Password is incorrect", -1)
        # token = login_obj.token
        if login.token.is_expired():
            session.delete(login.token)
            create_session_token(login, session)
        else:
            extend_token(login.token)
    return (login.token, login.type, 0)


def create_session_token(login_obj: Login, session):
    token_key = secrets.token_hex(16)
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


def get_token(key: str, session) -> SessionToken:
    stmt = select(SessionToken).where(SessionToken.token_key == key)
    token = session.execute(stmt).scalar_one_or_none()
    if token is None or token.is_expired():
        raise ExpiredToken("Token is invalid")
    return token


def extend_token(token: SessionToken):
    token.expires_at += datetime.timedelta(hours=2)


def get_user(key: str) -> tuple[StudentData | ProfessorData | DeanData, str]:
    with Session() as session:
        token = get_token(key, session)
        if token.is_expired():
            raise ExpiredToken("Token Invalid")
        login = token.login
        extend_token(token)
        session.commit()
        usrtype = Tables[login.type]
        return session.get(usrtype, login.uid), login.type


##These functions are just for testing
def get_login(uid, type) -> Login:
    with Session() as session:
        stmt = select(Login).where(Login.uid == uid, Login.type == type)
        element = session.execute(stmt).fetchall()
        if len(element) < 1:
            return "Something went Wrong"
        return element[0].Login


def get_token_from_udata(uid, type):
    login = get_login(uid, type)
    with Session() as session:
        return session.merge(login).token.token_key
