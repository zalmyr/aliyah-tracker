from sqlalchemy.orm import Session
from . import models, schemas

# --- People ---
def create_person(db: Session, person: schemas.PersonCreate):
    db_person = models.Person(**person.dict())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

def get_people(db: Session):
    return db.query(models.Person).all()

def update_person(db: Session, person_id: int, updates: dict):
    db_person = db.query(models.Person).filter(models.Person.id == person_id).first()
    if not db_person:
        return None
    for field, value in updates.items():
        setattr(db_person, field, value)
    db.commit()
    db.refresh(db_person)
    return db_person

# --- Aliyot ---
def create_aliyah(db: Session, aliyah: schemas.AliyahCreate):
    db_aliyah = models.Aliyah(**aliyah.dict())
    db.add(db_aliyah)
    db.commit()
    db.refresh(db_aliyah)
    return db_aliyah

def get_aliyot(db: Session):
    return db.query(models.Aliyah).all()

# --- Relationships ---
def create_relationship(db: Session, rel: schemas.RelationshipCreate):
    db_rel = models.Relationship(**rel.dict())
    db.add(db_rel)
    db.commit()
    db.refresh(db_rel)
    return db_rel

def get_relationships(db: Session):
    return db.query(models.Relationship).all()

def update_relationship(db: Session, rel_id: int, updates: dict):
    db_rel = db.query(models.Relationship).filter(models.Relationship.id == rel_id).first()
    if not db_rel:
        return None
    for field, value in updates.items():
        setattr(db_rel, field, value)
    db.commit()
    db.refresh(db_rel)
    return db_rel
