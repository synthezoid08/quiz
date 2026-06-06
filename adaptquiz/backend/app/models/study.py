from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func

from app.db.base_class import Base


class Flashcard(Base):
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("note.id"), nullable=True)
    student_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    front = Column(String, nullable=False)
    back = Column(String, nullable=False)
    next_review_date = Column(DateTime(timezone=True), nullable=True)
    interval = Column(Integer, default=0)  # Days until next review
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ConceptMap(Base):
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("note.id"), nullable=False)
    graph_data = Column(JSON, nullable=False)  # Nodes and edges
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class StudyPlan(Base):
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    schedule_data = Column(JSON, nullable=False)
    target_exam_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
