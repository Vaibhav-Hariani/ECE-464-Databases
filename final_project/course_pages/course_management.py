import streamlit as st
from db_functions import *
from db_objects import *


def professor_courseman(key: SessionToken):
    courses, archetypes, semesters, status = get_prof_courses(key)
    running_i = []
    labels = []
    semester = st.selectbox("Select a semester", [semester[0] for semester in semesters])    

    for i in range(len(courses)):
        if courses[i].running and courses[i].semester_id == semester.id:
            running_i.append(i)
            labels.append(archetypes[i].course_name)
    tabs = st.tabs(labels)

    for i in range(len(tabs)):
        with tabs[i]:
            course = courses[running_i[i]]
            assignment_types = get_assign_specs(course)
            no_el = "Course View"
            full_list = assignment_types + [no_el]
            assign_type = st.selectbox("Select an Assignment Type", [a_spec for a_spec in full_list])    
            if assign_type == no_el:
                grades = get_grades(course)
                pass
                # st.stop()
            else:
                grades = get_
            # st.write()
            raw, curved = st.columns(2)
            with raw:
                st.line_chart(grades[1], x_label="Students (Sorted)", y_label="Grades (Raw)")
            with curved:
                st.text_input("Want to test a new curve? Input Here")
                st.line_chart(grades[0], x_label="Students (Sorted)", y_label="Grades (Curved)")

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
    utype = st.session_state["st_utype"]
    # user, utype = get_user(token.token_key)
    runner_table[utype](token.token_key)
