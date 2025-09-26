from pydantic import BaseModel
from datetime import date

class PersonBase(BaseModel):
    english_name: str
    hebrew_name: str | None = None
    notes: str | None = None

class PersonCreate(PersonBase):
    pass

class Person(PersonBase):
    id: int
    class Config:
        orm_mode = True

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
        orm_mode = True

class RelationshipBase(BaseModel):
    relation_type: str
    person_id: int
    related_person_id: int

class RelationshipCreate(RelationshipBase):
    pass

class Relationship(RelationshipBase):
    id: int
    class Config:
        orm_mode = True
