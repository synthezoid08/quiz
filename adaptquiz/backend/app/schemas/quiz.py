from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class QuestionBase(BaseModel):
    question_type: str
    content: str
    options: Optional[Dict] = None
    correct_answer: str
    explanation: Optional[str] = None
    difficulty_weight: float = 1.0

class QuestionResponse(QuestionBase):
    id: int
    quiz_id: int
    model_config = {"from_attributes": True}

class QuizBase(BaseModel):
    title: str
    difficulty: str = "Medium"
    is_adaptive: bool = False

class QuizCreate(BaseModel):
    note_id: int
    difficulty: str = "Medium"
    question_count: int = 5
    is_adaptive: bool = False

class QuizResponse(QuizBase):
    id: int
    creator_id: int
    created_at: datetime
    questions: List[QuestionResponse] = []
    
    model_config = {"from_attributes": True}
