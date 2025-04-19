from flask import request
from flask import Flask, make_response
from sqlalchemy.exc import IntegrityError
from objects import *



Tables = {"Student": (StudentData, StudentLogin),
          "Professor": (ProfessorData, ProfessorLogin),
          "Dean": {DeanData, DeanLogin}}

@app.route("/create_user", methods=['POST'])
def create_user():
    error = None
    uid = None
    ##Need to implement a security layer to guarantee 
    # this is a valid request. 
    try:
        type = request.form['obj_class']
        match type:
            case 'Student':
                uid = create_student(request.form)
            case 'Dean':
                uid = create_dean(request.form)
            case 'Professor':
                uid = create_professor(request.form)
            case _:
                return (-1, 400)
    except:
        return (-1, 400)
    if(uid < 0):
        return ("Data Already Exists!", 405)
    return uid

##safety function
def create_student(data: dict):
    try:
        student = StudentData(data['name'], data['email'])
        db.session.add(student)
    except IntegrityError:
        return -1
    try:
        Login = StudentLogin(data['uname'],data['pass'], student.id)
        db.session.add(Login)
    except IntegrityError:
        return -1 
    return Login.id

def create_dean(data: dict):
    student = StudentData(data['name'], data['email'])
    db.session.add(student)
    Login = StudentLogin(data['uname'],data['pass'], student.id)
    db.session.add(Login)
    return Login.id

##safety function
def create_professor(data: dict):
    student = StudentData(data['name'], data['email'])
    db.session.add(student)
    Login = StudentLogin(data['uname'],data['pass'], student.id)
    db.session.add(Login)
    return Login.id

