import streamlit as st
from db_functions import *
from db_objects import *



def hash_courses(obj: Courses):
    if obj:
        return str(obj.id) + obj.curve
    return 'None'

def hash_assign(obj: Assignment):
    if obj:
        return str(obj.id) + obj.curve + str(obj.weight)
    return 'None'

def hash_assignspec(obj: AssignSpec):
    if obj:
        return str(obj.id) + str(obj.weight)
    return 'None'

##Cache doesn't need to grow too large
@st.cache_data(hash_funcs={Courses: hash_courses, Assignment: hash_assign, AssignSpec: hash_assignspec},max_entries=5)
def cached_get_grades(course,assign_type,assignment):
    return get_grades(course,assign_type,assignment)    


def st_weight_adj(obj, new_weight):
    cached_get_grades.clear()
    update_weight(obj,new_weight)

def professor_courseman(key: str):
    courses, archetypes, semesters, status = get_courses(key)
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

            raw_grades = cached_get_grades(course, assign_type, assignment)

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

def student_courseman(key: str):
    courses, archetypes, semesters, status = get_courses(key)
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
            raw_grade = get_student_grade(key, course, assign_type, assignment)
            st.write(f"Your raw grade in this category is {raw_grade:0.2f}")
            if assignment:
                assignment_grade = get_submission(key,assignment)
                label = "Submit Work"
                if assignment_grade.submitted:
                    label = "Resubmit Work"
                    submitted_work = get_work(assignment_grade)
                    if submitted_work:
                        work, signature = submitted_work
                        st.warning("You've already submitted work for this assignment")
                        st.download_button("Download Your Submission", work,file_name=f"{signature}")
                    ##Allow users to download their own submission
                submission = st.file_uploader(label)
                if submission:
                    signature = submission.name
                    st.button("Submit Work", on_click=submit_work,args=(key,assignment_grade, submission,signature))



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
