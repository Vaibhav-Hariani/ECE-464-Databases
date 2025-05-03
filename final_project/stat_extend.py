from db_objects import *
from db_functions import get_raw_scores
from sqlalchemy import func, select
import statistics as stats

assign_funcs = {"mean": func.avg, "min": func.min, "max": func.max, "stddev": func.stddev}
course_funcs = {"mean": stats.mean, "min": min, "max": max, "stddev": stats.stdev, "range": range}


def is_valid(obj):
    if not isinstance(obj, Assignment) and not isinstance(obj, Courses):
        return False
    return True

def stat_struct(kw, obj: Assignment| Courses):
    if isinstance(obj, Courses):
        grades = get_raw_scores(Courses)
        return course_funcs[kw](grades)
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
