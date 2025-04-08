import flask
from flask import request

from objects import *

@app.route("/create_user", methods=['POST'])
def create_user():
    error=None
    uid = None
    ##Need to implement a security layer to guarantee 
    # this is a valid request. 

    try:
        type = request.form['obj_class']
        
    
##safety function
def create_student(data: dict):
    student = StudentData(data['name'], data['email'])
    db.session.add(student)
    Login = StudentLogin(data['uname'],data['pass'], student.id)
    db.session.add(Login)
    return Login.id

