from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import crud, schemas
from ..database import get_db
from ..auth import verify_api_key

router = APIRouter(
    prefix="/notes",
    tags=["notes"],
    dependencies=[Depends(verify_api_key)]
)

@router.post("", response_model=schemas.Note, status_code=status.HTTP_201_CREATED)
def create_note(note: schemas.NoteCreate, db: Session = Depends(get_db)):
    return crud.create_note(db=db, note=note)

@router.get("", response_model=List[schemas.Note])
def read_notes(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    return crud.get_notes(db, skip=skip, limit=limit)

@router.get("/search", response_model=List[schemas.Note])
def search_notes(
    tag: Optional[str] = Query(None, description="Filter by tag (exact match)"),
    q: Optional[str] = Query(None, description="Filter by keyword (case-insensitive substring)"),
    db: Session = Depends(get_db)
):
    return crud.search_notes(db=db, tag=tag, q=q)

@router.get("/{note_id}", response_model=schemas.Note)
def read_note(note_id: int, db: Session = Depends(get_db)):
    db_note = crud.get_note(db, note_id=note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_note

@router.put("/{note_id}", response_model=schemas.Note)
def update_note(note_id: int, note: schemas.NoteUpdate, db: Session = Depends(get_db)):
    db_note = crud.update_note(db, note_id=note_id, note=note)
    if db_note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_note

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    success = crud.delete_note(db, note_id=note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
