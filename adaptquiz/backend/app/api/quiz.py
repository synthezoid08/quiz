from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.quiz import Quiz, Question
from app.models.note import Note
from app.models.user import User
from app.schemas.quiz import QuizCreate, QuizResponse
from app.services.ai_pipeline import generate_quiz_from_note

router = APIRouter()

@router.post("/generate", response_model=QuizResponse)
def generate_quiz(
    request: QuizCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    note = db.query(Note).filter(Note.id == request.note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
        
    if note.status != "PROCESSED":
        raise HTTPException(status_code=400, detail="Note must be PROCESSED before generating a quiz.")

    # 1. Trigger AI generation
    ai_result = generate_quiz_from_note(request.note_id, request.difficulty)
    
    # In a real implementation, `ai_result` would be parsed JSON of questions.
    # For scaffolding, we generate dummy questions.
    
    db_quiz = Quiz(
        creator_id=current_user.id,
        title=f"Quiz for {note.title}",
        difficulty=request.difficulty,
        is_adaptive=request.is_adaptive
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    
    # Dummy Question logic mapping to AI result placeholder
    dummy_q = Question(
        quiz_id=db_quiz.id,
        question_type="MCQ",
        content="What is the main topic of this document?",
        options={"A": "Option 1", "B": "Option 2", "C": "Option 3", "D": "Option 4"},
        correct_answer="A",
        explanation="This is an AI generated explanation scaffolding.",
        difficulty_weight=1.0
    )
    db.add(dummy_q)
    db.commit()
    db.refresh(db_quiz)
    
    return db_quiz

@router.get("/", response_model=List[QuizResponse])
def get_quizzes(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    quizzes = db.query(Quiz).filter(Quiz.creator_id == current_user.id).all()
    return quizzes
