import streamlit as st
from db_functions import *
from db_objects import *


def professor_courseman(key: SessionToken):
    courses, archetypes, semesters, status = get_prof_courses(key)
    running_i = []
    labels = []
    semester = st.selectbox(
        "Select a semester", [semester[0] for semester in semesters]
    )

    for i in range(len(courses)):
        if courses[i].running and courses[i].semester_id == semester.id:
            running_i.append(i)
            labels.append(archetypes[i].course_name)

    if len(labels) == 0:
        st.warning("No Data for Professor")
        st.stop()

    tabs = st.tabs(labels)
    for i in range(len(tabs)):
        with tabs[i]:
            course = courses[running_i[i]]
            assignment_types = get_assign_specs(course)
            assign_type = st.selectbox("Assignment Type", assignment_types, index=None)
            assignment = None
            data = course
            if assign_type:
                assignments = get_assignments(assign_type)
                data = assign_type
                if len(assignments) > 0:
                    assignment = st.selectbox("Assignment", assignments, index=None)
                    if assignment:
                        data = assignment
                else:
                    st.warning("No Data For This Assignment Type")
                    st.stop()

            curve = "x"

            enabled = (not assign_type) or assignment
            if enabled:
                curve = data.curve
                num_cols = 2
            else:
                num_cols = 1
                st.warning(
                    "Curves not supported for this element. Curves can only be applied to specific assignments or course-wide."
                )
            text_box, button_box = st.columns(2, vertical_alignment="bottom")
            curve = text_box.text_input(
                "Using Curve:", value=curve, disabled=(not enabled)
            )
            button_box.button(
                "Apply this curve",
                on_click=assign_curve,
                args=(data, curve),
                icon=":material/done_outline:",
                disabled=(not enabled),
            )

            if assign_type:
                text_box, button_box = st.columns(2, vertical_alignment="bottom")
                weight = data.weight
                test_weight = text_box.text_input("Weight:", value=str(weight))
                try:
                    button_box.button(
                        "Update Weight",
                        on_click=update_weight,
                        args=(data, float(test_weight)),
                        icon=":material/done_outline:",
                    )
                except:
                    st.error("Invalid Input for weight")

            raw_grades = get_grades(course, assign_type, assignment)

            cols = st.columns(num_cols)
            # st.write("Something")
            with cols[0]:
                st.line_chart(
                    raw_grades, x_label="Students (Sorted)", y_label="Grades (Raw)"
                )
            if enabled:
                with cols[1]:
                    try:
                        curved_grades = [
                            apply_curve(curve, score, data) for score in raw_grades
                        ]
                        st.line_chart(
                            curved_grades,
                            x_label="Students (Sorted)",
                            y_label="Grades (Curved)",
                        )
                    except:
                        st.error(
                            "Curve Failed to Apply: For a guide, check ****. Remember, X should be the only variable."
                        )


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
