from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey,
    Boolean, Float, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Quiz(Base):
    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    title = Column(String, index=True)
    difficulty = Column(String, default="Medium")
    is_adaptive = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    questions = relationship(
        "Question", back_populates="quiz", cascade="all, delete-orphan"
    )


class Question(Base):
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quiz.id"), nullable=False)
    question_type = Column(String)  # MCQ, TF, FIB, DESC
    content = Column(String, nullable=False)
    options = Column(JSON, nullable=True)  # For MCQs
    correct_answer = Column(String, nullable=False)
    explanation = Column(String, nullable=True)
    difficulty_weight = Column(Float, default=1.0)

    quiz = relationship("Quiz", back_populates="questions")


class QuizAttempt(Base):
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quiz.id"), nullable=False)
    score = Column(Float, default=0.0)
    accuracy = Column(Float, default=0.0)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
