# This file imports all models so that Alembic can detect them.
from app.db.base_class import Base  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.note import Note  # noqa: F401
from app.models.quiz import Quiz, Question, QuizAttempt  # noqa: F401
from app.models.study import Flashcard, ConceptMap, StudyPlan  # noqa: F401
