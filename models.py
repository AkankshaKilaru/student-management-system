from sqlalchemy import Column, Integer, String
from database import Base

# Student Table
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    course = Column(String)
    marks = Column(Integer)
    hallticket = Column(String)
    attendance = Column(Integer)

# User Table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String, default="user")  # admin or user