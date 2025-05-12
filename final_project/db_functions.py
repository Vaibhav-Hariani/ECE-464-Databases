from sqlalchemy.exc import IntegrityError
from sqlalchemy import bindparam, select, delete, inspect, update
import secrets
from db_objects import *
from curve_parser import apply_curve, get_raw_scores, aggregate_score, test_parse
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
    course_name = courseinfo["name"]
    course_code = courseinfo["course_code"]
    with Session() as session:
        user, utype = get_user(key, session)
        try:
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
            user, utype = get_user(key, session)
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


def assign_curve(obj: Courses | Assignment, curve_str) -> tuple[str, int]:
    msg, result = test_parse(curve_str)
    if result != 0:
        return msg, result
    with Session.begin() as session:
        obj = session.merge(obj)
        obj.curve = curve_str
        session.commit()
        return msg, result


## Courtesy of Gemini
## Made significant modifications
@event.listens_for(Assignment, "after_update")
def assignment_after_update(mapper, connection, target: Assignment):
    """
    After an Assignment is updated, check if the curve changed.
    If so, update the curved_score for all related AssignmentGrade records.
    """
    session = Session.object_session(target)
    if not session:
        # Cannot proceed without a session context
        # This might happen in bulk updates outside a session flush context.
        # Consider alternative strategies (like DB triggers) if this is a common case.
        raise Exception(f"No Session found to update grades on assignment")

    insp = inspect(target)
    curve_history = insp.attrs.curve.history
    weight_history = insp.attrs.weight.history

    # Check if 'curve' was actually changed in this update
    if curve_history.has_changes() or weight_history.has_changes():
        assignment_id = target.id
        new_curve = target.curve
        new_weight = target.weight
        print(
            f"Curve changed for Assignment {assignment_id}. Updating related AssignmentGrade curved_scores..."
        )

        # --- Strategy: Fetch grades, calculate in Python, update in bulk ---
        # This keeps curve logic in Python but requires fetching IDs and grades first.
        stmt_select_grades = select(AssignmentGrade.id, AssignmentGrade.grade).where(
            AssignmentGrade.assign_id == assignment_id
        )

        # Execute within the existing transaction context if possible
        results = connection.execute(stmt_select_grades).fetchall()

        if not results:
            print(f"No AssignmentGrades found for Assignment {assignment_id}.")
            return  # Nothing to update

        updates = []

        if curve_history.has_changes():
            for grade_id, original_grade in results:
                new_curved_score = new_weight * apply_curve(
                    new_curve, original_grade, target
                )
                updates.append({"id": grade_id, "curved_score": new_curved_score})
        else:
            for grade_id, original_grade in results:
                new_curved_score = new_weight * original_grade
                updates.append({"id": grade_id, "curved_score": new_curved_score})

        # Perform bulk update
        # Note: Use connection directly as we are inside the event listener flush process
        stmt_update = (
            update(AssignmentGrade)
            .where(AssignmentGrade.id == bindparam("_id"))
            .values(curved_score=bindparam("curved_score"))
        )

        # Map the keys in `updates` to the bindparam names
        bind_updates = [
            {"_id": u["id"], "curved_score": u["curved_score"]} for u in updates
        ]

        connection.execute(stmt_update, bind_updates)
        print(
            f"Updated curved_score for {len(updates)} AssignmentGrade records for Assignment {assignment_id}."
        )


@event.listens_for(AssignmentGrade, "before_insert")
@event.listens_for(AssignmentGrade, "before_update")
def assignment_grade_before_save(mapper, connection, target: AssignmentGrade):
    session = Session.object_session(target)
    if not session:
        print(
            f"Warning: No session found for AssignmentGrade {target.id or '(new)'} during before_save. Cannot set curved_score."
        )
        return

    # Check if 'grade' is set or being changed
    insp = inspect(target)
    grade_history = insp.attrs.grade.history
    recalculate = (insp.transient or insp.pending) or grade_history.has_changes()
    if recalculate:
        parent_assignment = target.assignment
        grade = target.grade
        if grade is None:
            grade = 0.0
        new_score = apply_curve(parent_assignment.curve, grade, parent_assignment)
        target.curved_score = parent_assignment.weight * new_score


##Depending on future work, may need to add ability to upload
def submit(token: str, assignment: Assignment) -> tuple[String, int]:
    with Session.begin() as session:
        user, utype = get_user(token, session)
        if utype != "student":
            return ("Not a Student", -2)
        stmt = select(AssignmentGrade).where(
            AssignmentGrade.student_id == user.id,
            AssignmentGrade.assign_id == assignment.id,
        )
        gradable = session.execute(stmt).scalar()
        gradable.submitted = True
        gradable.time_submitted = get_time()
    return ("Success!", 0)


def grade(key: str, submission: AssignmentGrade, grade) -> tuple[AssignmentGrade, int]:
    with Session() as session:
        user, utype = get_user(key, session)
        if utype != "professor":
            return ("Not a Professor", -2)

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


##Uncurved grades
def get_grades(
    course: Courses = None, assign_type: AssignSpec = None, assign: Assignment = None
):
    with Session() as session:
        course = session.merge(course)
        students = course.students
        raw_grades = []
        if assign or assign_type:
            raw_grades = [get_student_grade(None,course,assign_type,assign,use_curve=False,uid=student.id) for student in students]
        elif course:
            raw_grades = aggregate_score(course,session)
        raw_grades.sort()
        return raw_grades


def get_student_grade(
    key: str | None, course: Courses, assign_type=None,
    assign=None, use_curve=False, uid=None
) -> float:
    with Session() as session:
        if uid is None:
            user, utype = get_user(key, session)
            uid = user.id
        if assign:
            return get_assignment_grade(None, assign, uid,use_curve=use_curve)
        elif assign_type:
            return get_category_grade(None, assign_type, uid,use_curve=use_curve)
        elif course:
            course = session.merge(course)
            grade = get_raw_scores(course, uid, session)
            if use_curve: 
                grade = apply_curve(course.curve,grade,course)
            return grade

def update_weight(obj, new_weight):
    with Session() as session:
        obj = session.merge(obj)
        obj.weight = new_weight
        session.commit()


def get_assignment_grade(key: str | None, assign: Assignment, uid=None, use_curve=True):
    uid = uid
    utype = "student"
    with Session() as session:
        if uid is None:
            user, utype = get_user(key, session)
            uid = user.id
        if utype != "student":
            return ("Invalid User", 0)

        curve = assign.curve
        stmt = select(AssignmentGrade.grade).where(
            AssignmentGrade.student_id == uid, AssignmentGrade.assign_id == assign.id
        )
        grade = session.execute(stmt).scalar_one_or_none()
        if use_curve:
            return apply_curve(curve, grade, assign)
        return grade

def get_category_grade(key: str | None, spec: AssignSpec, uid=None, use_curve=True) -> float:
    with Session() as session:
        uid = uid
        utype = "student"
        if uid is None:
            user, utype = get_user(key, session)
            uid = user.id
        if utype != "student":
            return ("Invalid User", 0)
        assign_list = session.merge(spec).assignments
        grade = 0
        for assign in assign_list:
            lgrade = get_assignment_grade(None, assign, uid, use_curve)
            lgrade *= assign.weight
            grade += lgrade
        return grade

def get_submission(key: str, assign: Assignment) -> AssignmentGrade:
    with Session() as session:
        user, utype = get_user(key, session)
        if utype != "student":
            return ("Invalid User", 0)
        stmt = select(AssignmentGrade).where(AssignmentGrade.assign_id==assign.id,AssignmentGrade.student_id==user.id)
        return session.execute(stmt).scalar_one_or_none()

def get_work(obj: AssignmentGrade):
    with Session() as session:
        obj = session.merge(obj)
        if(obj.submission):
            return obj.submission.raw_data, obj.submission.signature
    return None
##Grades are stored in 0-100 format.
##This needs to take those values, and curve them according to

def submit_work(key: str, grade: AssignmentGrade, work,signature):
    with Session.begin() as session:
        grade = session.merge(grade)
        # if grade.submitted:
        #     submission = grade.submission
        #     submission.raw_data = work
        # else:
        bytes = work.read()
        data = AssignmentGradeData(assign_id=grade.id,raw_data=bytes,signature=signature)
        session.add(data)
        grade.submitted = True
        grade.time_submitted = get_time()



def get_time():
    return datetime.datetime.now()


##Course management
def get_courses(
    key: str,
) -> tuple[List[Courses], List[CourseArchetype], List[Semesters], int]:
    with Session() as session:
        user, utype = get_user(key, session)
        if utype == "dean":
            return "Invalid UserType"
        courses = user.courses
        archetypes = []
        semesters = []
        for course in courses:
            semesters.extend(get_semester(course.semester_id)[0])
            archetypes.append(course.archetype)
        return (courses, archetypes, semesters, 0)


def reg_student(key: str, course_data: dict | None = None, course_id=None):
    with Session.begin() as session:
        student = get_user(key,session)[0]

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
            extend_token(login.token, session)
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


def extend_token(token: SessionToken, session):
    token.expires_at += datetime.timedelta(hours=2)


def get_user(key: str, session) -> tuple[StudentData | ProfessorData | DeanData, str]:
    token = get_token(key, session)
    if token.is_expired():
        raise ExpiredToken("Token Invalid")
    login = token.login
    extend_token(token, session)
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
