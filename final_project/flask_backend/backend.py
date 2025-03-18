from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import MappedAsDataclass
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Base(MappedAsDataclass, DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
