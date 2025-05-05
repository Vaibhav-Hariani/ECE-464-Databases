##Quick script to populate and test database creation by hammering it with an array
import db_functions
from db_objects import *

PAGE = "http://127.0.0.1:5000"
import random
from wonderwords import RandomWord


def add_password():
    """Generates a simple pseudo-random password."""
    random_punct = ["!", "@", "_", "$", "&", "+"]
    r = RandomWord()
    passw = r.word(include_parts_of_speech=["verbs"])
    passw += random.choice(random_punct)
    passw += r.word(include_parts_of_speech=["nouns"])
    passw += random.choice(random_punct)
    return passw


def create_element(element):
    # --- Lists of names for realistic generation ---
    ##These lists are courtesy of Gemini
    first_names = [
        "Olivia",
        "Liam",
        "Emma",
        "Noah",
        "Amelia",
        "Oliver",
        "Ava",
        "Elijah",
        "Sophia",
        "Mateo",
        "Isabella",
        "Lucas",
        "Mia",
        "Levi",
        "Charlotte",
        "Asher",
        "Luna",
        "James",
        "Gianna",
        "Leo",
        "Aurora",
        "Grayson",
        "Harper",
        "Ezra",
        "Evelyn",
        "Luca",
        "Aria",
        "Ethan",
        "Ellie",
        "Aiden",
        "Mila",
    ]
    last_names = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Garcia",
        "Miller",
        "Davis",
        "Thompson",
        "White",
        "Harris",
        "Sanchez",
        "Clark",
        "Ramirez",
        "Lewis",
        "Robinson",
        "Walker",
        "Young",
        "Allen",
        "King",
    ]
    fname = random.choice(first_names)
    lname = random.choice(last_names)
    username = fname + "_" + lname
    email = username + "@copperonion.edu"
    element["name"] = fname + " " + lname
    element["uname"] = username
    element["email"] = email
    element["pass"] = add_password()


def populate_students(NUM_STUDENTS=21):
    for i in range(NUM_STUDENTS):
        element = {"obj_class": "student"}
        create_element(element)
        response = db_functions.create_user(element)
        print(response)


def login_test(user: StudentData | ProfessorData | DeanData, dtype: str):
    subject_creds = db_functions.get_login(user.id, dtype)
    print(subject_creds)
    new_pass = subject_creds.password + "@"
    successful_login = db_functions.login(subject_creds.uname, subject_creds.password)
    print(successful_login[1])
    print(db_functions.login(subject_creds.uname, new_pass))


def populate_professors():
    major_id = db_functions.create_major("Electrical Engineering")
    element = {"obj_class": "professor", "major_id": major_id}
    ##Starting with just two professors
    fname = "Deli"
    lname = "Katz"
    username = fname + "_" + lname
    email = username + "@copperonion.edu"
    element["name"] = fname + " " + lname
    element["uname"] = username
    element["email"] = email
    element["pass"] = "VaibhavGetsAnA!"
    ret = db_functions.create_user(element)
    print(ret[0])

    fname = "NH"
    lname = "Keene"
    username = fname + "_" + lname
    email = username + "@copperonion.edu"
    element["name"] = fname + " " + lname
    element["uname"] = username
    element["email"] = email
    element["pass"] = "VaibhavGetsAnA!"
    ret = db_functions.create_user(element)
    print(ret[0])


def create_course(prof: ProfessorData):
    login_creds = db_functions.get_login(prof.id, "professor")
    token = db_functions.login(login_creds.uname, login_creds.password)
    key = token[0].token_key
    semester_id, status = db_functions.create_semester("Spring 2025")
    if status != 0:
        print("something went wrong creating semester")
    course_info = {"name": "Daterbasers", "course_code": "ECE-464", "section": "A"}
    gen_course, status = db_functions.create_gen_course(key, course_info)
    if status != 0:
        print("Something went wrong creating the general course")
    course_info["semester id"] = semester_id
    course_info["breakdown"] = ""
    return db_functions.create_course_instance(course_info, key)


if __name__ == "__main__":
    # populate_students()
    Students = db_functions.table_loader(StudentData)
    for student in Students:
        print(student.name)
        print("Done printing students")
    # populate_professors()
    Professors = db_functions.table_loader(ProfessorData)
    for prof in Professors:
        print(prof.name)
        login = db_functions.get_login(prof.id, "professor")
        print(login.uid)
        print(f"{login.uname} {login.password}")

    login_test(Professors[-1], "professor")
    course, status = create_course(Professors[0])

    breakdown = [("Exams", 0.4), ("Homework", 0.4), ("Participation", 0.1)]
    breakdown = db_functions.create_breakdown(course.id, breakdown)

    assign_args = {"weight": 0.5, "name": "HW #1", "due_date": db_functions.get_time()}

    assignment, status = db_functions.new_assignment(course.id, "Homework", assign_args)

    tokens = [
        db_functions.get_token_from_udata(student.id, "student") for student in Students
    ]

    [db_functions.reg_student(token, course_id=course.id) for token in tokens]
    db_functions.create_grades(assignment)

    grades = db_functions.table_loader(AssignmentGrade)
    [db_functions.submit(token, assignment) for token in tokens]

    i = 0.0
    prof_token = db_functions.get_token_from_udata(Professors[0].id, "professor")
    for student_grade in grades[:-10]:
        grade, status = db_functions.grade(prof_token, student_grade, i)
        i += 2
    for student_grade in grades[-10:]:
        grade, status = db_functions.grade(prof_token, student_grade, i)
        i += 4

    for token in tokens:
        print(db_functions.get_student_grade(token, course))

    curve = "x * 5 / stddev"
    db_functions.assign_curve(assignment, curve)
    curve = "x / 4"
    db_functions.assign_curve(course, curve)
    for token in tokens:
        print(db_functions.get_student_grade(token, course))
