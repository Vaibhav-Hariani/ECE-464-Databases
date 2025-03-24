from orm import *
from sqlalchemy import select, func, distinct, desc
from sqlalchemy.orm import Session
import pytest

# Helper function


def cmp(orm_result, sql_result):
    assert len(orm_result) == len(
        sql_result
    ), f"orm result was not the same size as sql_result"
    for entry in sql_result:
        # print(entry)
        el = entry in orm_result
        assert (
            el
        ), f"Element Error: \n {entry} was present in orm return \n not present in the raw sql query"


def test_one():
    data_sel = select(Boat.bid, Boat.bname, func.count(Boat.bid))
    table_join = data_sel.join_from(Reservation, Boat)
    stmt = table_join.group_by(Reservation.bid, Boat.bid, Boat.bname)

    orm_result = conn.execute(stmt.order_by(Boat.bid)).fetchall()
    txt = """SELECT boats.bid, boats.bname, COUNT(boats.bid) 
    FROM reserves JOIN boats ON boats.bid=reserves.bid 
    GROUP BY reserves.bid, boats.bname, boats.bid"""
    sql_result = conn.execute((text(txt))).fetchall()
    # print("orm_data: ")
    cmp(orm_result, sql_result)


def test_two():
    sub_query = select(distinct(func.count(Boat.bid))).where(Boat.color == "red")
    data_sel = select(Sailor.sname, Sailor.sid)
    table_join = data_sel.join_from(Boat, Reservation)
    table_join = table_join.join(Sailor)
    stmt = table_join.where(Boat.color == "red")
    stmt = stmt.group_by(Sailor.sid).having(func.count(Boat.bid) == sub_query)
    orm_result = conn.execute(stmt).fetchall()
    txt = """select sailors.sname, sailors.sid from reserves
	inner join boats
		on boats.bid = reserves.bid
	inner join sailors 
		on sailors.sid = reserves.sid
	where boats.color = 'red'
	group by sailors.sid
	having COUNT(boats.bid) = (select distinct COUNT(boats.bid) from boats where boats.color = 'red');
"""
    sql_result = conn.execute((text(txt))).fetchall()
    print(stmt)
    cmp(orm_result, sql_result)


def test_three():
    sub_query = select(Reservation.sid).join(Boat).where(Boat.color != "red")
    data_sel = select(Sailor.sname, Sailor.sid)
    table_join = data_sel.join_from(Reservation, Boat).join(Sailor)
    stmt = table_join.where(Boat.color == "red").where(Sailor.sid.not_in(sub_query))
    stmt = stmt.group_by(Sailor.sid)
    txt = """     select sailors.sname, sailors.sid from reserves r
        inner join boats b
            on b.bid=r.bid
        inner join sailors 
            on sailors.sid = r.sid
        where b.color = 'red' and sailors.sid not in (select r.sid from reserves r inner join boats b on b.bid=r.bid where b.color != 'red')
        group by sailors.sid
"""
    orm_result = conn.execute(stmt).fetchall()
    sql_result = conn.execute((text(txt))).fetchall()
    cmp(orm_result, sql_result)


def test_four():
    stmt = select(Reservation.bid, func.count(Reservation.bid)).group_by(
        Reservation.bid
    )
    stmt = stmt.order_by(func.count(Reservation.bid).desc())
    txt = """
    select reserves.bid, COUNT(reserves.bid) 
    from reserves group by reserves.bid order 
    by COUNT(reserves.bid) desc limit 1
    """
    orm_result = conn.execute(stmt.limit(1)).fetchall()
    sql_result = conn.execute(text(txt)).fetchall()


# if __name__ == "__main__":
#     test = TestClass()
#     test.test_one()
