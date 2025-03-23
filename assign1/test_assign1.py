from orm import *
from sqlalchemy import select, func, distinct
from sqlalchemy.orm import Session
import pytest

##Helper function
def cmp(orm_result, sql_result):
        assert len(orm_result) == len(sql_result), f"orm result was not the same size as sql_result"
        for entry in sql_result:    
            # print(entry)
            el = entry in orm_result
            assert el, f"Element Error: \n {entry} was present in orm return \n not present in the raw sql query"


def test_one():
    data_sel= select(Boat.bid, Boat.bname, func.count(Boat.bid))
    table_join = data_sel.join_from(Reservation, Boat)
    stmt = table_join.group_by(Reservation.bid, Boat.bid, Boat.bname)
    
    orm_result = conn.execute(stmt.order_by(Boat.bid)).fetchall()
    txt = '''SELECT boats.bid, boats.bname, COUNT(boats.bid) 
    FROM reserves JOIN boats ON boats.bid=reserves.bid 
    GROUP BY reserves.bid, boats.bname, boats.bid'''
    sql_result= conn.execute((text(txt))).fetchall()
    # print("orm_data: ")
    cmp(orm_result, sql_result)

def test_two():
    sub_query = select(Boat.bid, distinct(func.count(Boat.bid)))
    # sub_query = select(func.count(Boat.bid).distinct).=where(Boat.color = 'red') 

    data_sel= select(Sailor.sname, Sailor.sid)
    table_join = data_sel.join_from(Boat, Reservation)
    table_join = table_join.join(Sailor)
    stmt = table_join.where(Boat.color == 'red')
    stmt = stmt.group_by(Sailor.sid).having(sub_query.Boat.bid == 'Red')    
    orm_result = conn.execute(stmt.order_by(Boat.bid)).fetchall()
    txt = '''SELECT boats.bid, boats.bname, COUNT(boats.bid) 
    FROM reserves JOIN boats ON boats.bid=reserves.bid 
    GROUP BY reserves.bid, boats.bname, boats.bid'''
    sql_result= conn.execute((text(txt))).fetchall()
    print(stmt)
    cmp()


# if __name__ == "__main__":
#     test = TestClass()
#     test.test_one()
