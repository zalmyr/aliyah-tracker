from pydantic import BaseModel
from datetime import date

class PersonBase(BaseModel):
    english_name: str
    hebrew_name: str | None = None
    father_hebrew_name: str | None = None   # NEW
    notes: str | None = None

class PersonCreate(PersonBase):
    pass

class Person(PersonBase):
    id: int
    class Config:
        from_attributes = True  # Pydantic v2 fix

class AliyahBase(BaseModel):
    date: date
    parsha: str
    service: str
    aliyah_number: str
    reason: str | None = None
    person_id: int

class AliyahCreate(AliyahBase):
    pass

class Aliyah(AliyahBase):
    id: int
    class Config:
        from_attributes = True

class RelationshipBase(BaseModel):
    relation_type: str
    person_id: int
    related_person_id: int

class RelationshipCreate(RelationshipBase):
    pass

class Relationship(RelationshipBase):
    id: int
    class Config:
        from_attributes = True
