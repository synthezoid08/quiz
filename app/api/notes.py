from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.note import Note, NoteStatus
from app.models.user import User
from app.schemas.note import NoteCreate, NoteResponse
from app.services.ai_pipeline import process_document

router = APIRouter()


@router.get("/", response_model=List[NoteResponse])
def get_notes(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    notes = db.query(Note).filter(Note.user_id == current_user.id).all()
    return notes


@router.post("/upload", response_model=NoteResponse)
def upload_note(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    if not file.filename.endswith(('.pdf', '.txt')):
        raise HTTPException(
            status_code=400, detail="Only PDF and TXT files are supported currently."
        )

    # Save file locally (in production, use S3/Blob storage)
    import os
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = f"{upload_dir}/{file.filename}"
    
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Create DB entry
    db_note = Note(
        user_id=current_user.id,
        title=file.filename,
        file_type=file.filename.split('.')[-1],
        file_path=file_path,
        status=NoteStatus.PROCESSING
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    # Trigger processing (async in production, synchronous for now)
    try:
        process_document(file_path, db_note.id, current_user.id)
        db_note.status = NoteStatus.PROCESSED
    except Exception as e:
        db_note.status = NoteStatus.FAILED
        print(f"Error processing note: {e}")
        
    db.commit()
    db.refresh(db_note)

    return db_note
