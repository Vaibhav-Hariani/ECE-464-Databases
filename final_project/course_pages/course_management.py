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
            assign_type = st.selectbox("Select an Assignment Type", assignment_types, index=None)    
            assignment = None
            curve = course.curve
            data = course
            if assign_type:
                assignments = get_assignments(assign_type)
                if len(assignments) > 0:
                    assignment = st.selectbox("Select An Assignment", assignments,index=None)
                else:
                    st.warning("No Data For This Assignment Type")
                    st.stop()
                curve = 'x'
            if assignment and assign_type:
                curve = assignment.curve
                data = assignment
            if (not assign_type) or assignment:
                curve = st.text_input("Using Curve:", value=curve)                
            raw_grades = get_grades(course,assign_type,assignment)
            raw, curved = st.columns(2)
            # st.write("Something")
            with raw:
                st.line_chart(raw_grades, x_label="Students (Sorted)", y_label="Grades (Raw)")
            if (not assign_type) or assignment:
                with curved:
                    try:
                        curved_grades = [apply_curve(curve, score ,data) for score in raw_grades]
                        st.line_chart(curved_grades, x_label="Students (Sorted)", y_label="Grades (Curved)")
                    except:
                        st.error("Curve Failed to Apply: Remember, X should be the only variable.") 

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
