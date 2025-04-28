import streamlit as st
from db_functions import *
from db_objects import *




def professor_courseman(user: ProfessorData):
    courses = get_prof_courses(user)
    st.write(courses)
    pass


def student_courseman(user: StudentData):
    st.write("Coming Soon!")
    pass


def dean_courseman(user: DeanData):
    st.write("Coming Soon!")
    pass



runner_table = {
    "student": student_courseman,
    "professor": professor_courseman,
    "dean": dean_courseman,
}

if __name__ == "__main__":
    if "st_token" not in st.session_state:
        st.error("You shouldn't have access to this page!")
        st.stop()
    token = st.session_state["st_token"]
    user, utype = get_user(token.token_key)
    st.write(utype)
    runner_table[utype](user)

1