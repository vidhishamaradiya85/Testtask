from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from . import models, schemas

def get_note(db: Session, note_id: int):
    return db.query(models.Note).filter(models.Note.id == note_id).first()

def get_notes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Note).offset(skip).limit(limit).all()

def create_note(db: Session, note: schemas.NoteCreate):
    db_note = models.Note(**note.model_dump())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

def update_note(db: Session, note_id: int, note: schemas.NoteUpdate):
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not db_note:
        return None
    
    update_data = note.model_dump(exclude_unset=True)
    if update_data:
        for key, value in update_data.items():
            setattr(db_note, key, value)
        db.commit()
        db.refresh(db_note)
    return db_note

def delete_note(db: Session, note_id: int):
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if db_note:
        db.delete(db_note)
        db.commit()
        return True
    return False

def search_notes(db: Session, tag: str | None = None, q: str | None = None):
    query = db.query(models.Note)
    if tag:
        # SQLite JSON matching for tags using string contains (assuming tags is list of strings)
        query = query.filter(models.Note.tags.cast(models.String).contains(f'"{tag}"'))
    if q:
        query = query.filter(
            or_(
                models.Note.title.ilike(f"%{q}%"),
                models.Note.body.ilike(f"%{q}%")
            )
        )
    return query.all()
