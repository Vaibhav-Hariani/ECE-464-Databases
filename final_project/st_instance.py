import streamlit as st
from streamlit import runtime
import st_pages
from streamlit.web import cli as stcli
import sys
from time import sleep
from db_functions import *
from db_objects import *


# TODO: use azure login for security.
# In the meantime, simple session states and passwords will do
def log_in():
    username = st.text_input("Username", key="username")
    password = st.text_input("Password", key="password", type="password")
    if st.button("Login"):
        if not db_login(username, password):
            st.error("Username or Password False!")
        else:
            st.rerun()


def db_login(username, password):
    print(f"{username}, {password}")
    login_details = login(username, password)
    if login_details[-1] == 0:
        st.session_state["st_login"] = True
        st.session_state["st_token"] = login_details[0]
        st.session_state["st_utype"] = login_details[1]
        st.session_state["name"] = username

        return True
    else:
        return False


def log_out():
    st.session_state["st_login"] = False
    st.session_state["st_token"] = False
    st.session_state["st_utype"] = None
    st.success("Logged out!")
    sleep(5)
    st.rerun()


def runner():
    login_page = st.Page(log_in, title="Log in", icon=":material/login:")
    logout_page = st.Page(log_out, title="Log out", icon=":material/logout:")

    register_page = st.Page(
        "course_pages/add_drop.py",
        title="Add or Drop a Class",
        icon=":material/grading:",
    )
    course_page = st.Page(
        "course_pages/course_management.py",
        title="Existing Classes",
        icon=":material/grading:",
    )
    if st.session_state["st_login"]:

        pg = st.navigation(
            {
                "Course Management": [register_page, course_page],
                "Account": [logout_page],
                # "Assignment View": [assignment_page],
            }
        )
    else:
        st.header("Welcome to the Gradebook! Please enter your username and Password.")
        pg = st.navigation([login_page])
    pg.run()


if __name__ == "__main__":
    if runtime.exists():
        st.set_page_config(page_title="Cooper Gradebook", page_icon="🎓")
        if "st_login" not in st.session_state:
            st.session_state["st_login"] = False
            st.session_state["st_token"] = 0
            st.session_state["st_utype"] = None
            st.session_state["name"] = None

        runner()
    else:
        sys.argv = [
            "streamlit",
            "run",
            sys.argv[0],
        ]
        sys.exit(stcli.main())
