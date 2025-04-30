from db_objects import *
from sqlalchemy import func, select

# My extension for statistical function support
# This should be different behavior depending
# Currently, these functions are only supported for


def is_valid(obj):
    if not isinstance(obj, Assignment):
        return False
    return True


def mean(assign: Assignment):
    stmt = select(func.avg(AssignmentGrade.grade)).where(
        AssignmentGrade.assign_id == assign.id
    )
    with Session() as session:
        data = session.execute(stmt).scalar_one_or_none()
    if data is None:
        return 0
    return data


def min(assign: Assignment):
    stmt = select(func.min(AssignmentGrade.grade)).where(
        AssignmentGrade.assign_id == assign.id
    )
    with Session() as session:
        data = session.execute(stmt).scalar_one_or_none()
    if data is None:
        return 0
    return data

def max(assign: Assignment):
    stmt = select(func.max(AssignmentGrade.grade)).where(
        AssignmentGrade.assign_id == assign.id
    )
    with Session() as session:
        data = session.execute(stmt).scalar_one_or_none()
    if data is None:
        return 0
    return data


def range(assign: Assignment):
    stmt = select(func.max(AssignmentGrade.grade)).where(
        AssignmentGrade.assign_id == assign.id
    )
    with Session() as session:
        data = session.execute(stmt).scalar_one_or_none()
    if data is None:
        return 0
    return data

    return 0


def stddev(assign: Assignment):
    return 0
