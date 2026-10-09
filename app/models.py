import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, func
from app.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True, index=True)  # Represents student_id (e.g. S1001)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String, nullable=False, index=True)
    student_name = Column(String, nullable=False)
    code = Column(Text, nullable=False)
    error_trace = Column(Text, nullable=True)
    misconception_id = Column(String, nullable=True)
    misconception_name = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    explanation = Column(Text, nullable=True)
    exercise = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=func.now())
