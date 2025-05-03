from db_objects import *
from db_functions import get_raw_scores
from sqlalchemy import func, select
import statistics as stats

# My extension for statistical function support
# This should be different behavior depending
# Currently, these functions are only supported for


def course_mean(course: Courses):
    with Session() as session:
        course = session.merge(Courses)
        grades = get_raw_scores(course)
        return stats.mean(grades)
    
def course_max(course: Courses):
    with Session() as session:
        course = session.merge(Courses)
        grades = get_raw_scores(course)
        return max(grades)

def course_min(course: Courses):
    with Session() as session:
        course = session.merge(Courses)
        grades = get_raw_scores(course)
        return min(grades)

def course_range(course: Courses):
    with Session() as session:
        course = session.merge(Courses)
        grades = get_raw_scores(course)
        return range(grades)

def course_stddev(course: Courses):
    with Session() as session:
        course = session.merge(Courses)
        grades = get_raw_scores(course)
        return stats.stdev(grades)
    
assign_funcs = {"mean": func.avg, "min": func.min, "max": func.max, "stddev": func.stddev}
course_funcs = {"mean": course_mean, "min": course_min, "max": course_max, "stddev": course_stddev, "range": course_stddev}


def is_valid(obj):
    if not isinstance(obj, Assignment) and not isinstance(obj, Courses):
        return False
    return True

def stat_struct(kw, obj: Assignment| Courses):
    if isinstance(obj, Courses):
        return course_funcs(kw,obj)
    ##Behavior for assignments and assignments only
    if(kw == "range"):
        return stat_struct("max",obj) - stat_struct("min", obj)
    func = assign_funcs[kw]
    stmt = select(func(AssignmentGrade.grade)).where(
        AssignmentGrade.assign_id == obj.id
    )
    with Session() as session:
        data = session.execute(stmt).scalar_one_or_none()
    if data is None:
        return 0
    return data
