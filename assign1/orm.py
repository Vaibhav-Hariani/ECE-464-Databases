from __future__ import print_function

from sqlalchemy import create_engine, text


from sqlalchemy.orm import declarative_base, backref, relationship
from sqlalchemy import (
    Integer,
    String,
    Column,
    DateTime,
    ForeignKey,
    PrimaryKeyConstraint,
)

engine = create_engine(
    "postgresql+psycopg2://postgres:example@localhost:5432", echo=True
)
conn = engine.connect()

Base = declarative_base()


class Sailor(Base):
    __tablename__ = "sailors"

    sid = Column(Integer, primary_key=True)
    sname = Column(String)
    rating = Column(Integer)
    age = Column(Integer)

    def __repr__(self):
        return "<Sailor(id=%s, name='%s', rating=%s)>" % (
            self.sid,
            self.sname,
            self.age,
        )


class Boat(Base):
    __tablename__ = "boats"

    bid = Column(Integer, primary_key=True)
    bname = Column(String)
    color = Column(String)
    length = Column(Integer)

    reservations = relationship(
        "Reservation", backref=backref("boat", cascade="delete")
    )

    def __repr__(self):
        return "<Boat(id=%s, name='%s', color=%s)>" % (self.bid, self.bname, self.color)


class Reservation(Base):
    __tablename__ = "reserves"
    __table_args__ = (PrimaryKeyConstraint("sid", "bid", "day"), {})

    sid = Column(Integer, ForeignKey("sailors.sid"))
    bid = Column(Integer, ForeignKey("boats.bid"))
    day = Column(DateTime)

    sailor = relationship("Sailor")

    def __repr__(self):
        return "<Reservation(sid=%s, bid=%s, day=%s)>" % (self.sid, self.bid, self.day)


if __name__ == "__main__":
    print(conn.execute(text("SELECT * from sailors")).fetchall())
    print("Sucessfully Connected ")
