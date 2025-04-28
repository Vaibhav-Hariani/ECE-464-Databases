import streamlit as st
from db_functions import *
from db_objects import *




def professor_courseman(user: ProfessorData):
    courses, archetypes, semesters, status = get_prof_courses(user)
    running_i = []
    labels = []
    for i in range(len(courses)):
        if courses[i].running:
            running_i.append(i)
            labels.append(archetypes[i].course_name)
    tabs = st.tabs(labels)
    for i in range(len(tabs)):
        with tabs[i]:
            st.write(labels[i])
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
    runner_table[utype](user)
