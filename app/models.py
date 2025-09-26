from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base

class Person(Base):
    __tablename__ = "people"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    hebrew_name = Column(String, nullable=True)
    father_hebrew_name = Column(String, nullable=True)
    tribe = Column(String, nullable=False, default="ישראל")  # כהן / לוי / ישראל
    notes = Column(Text, nullable=True)

    aliyot = relationship("Aliyah", back_populates="person")

class Aliyah(Base):
    __tablename__ = "aliyot"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    parsha = Column(String, nullable=True)
    yomtov = Column(String, nullable=True)
    service = Column(String, nullable=False)  # Shacharit / Mincha
    aliyah_number = Column(String, nullable=False)  # Hebrew
    reason = Column(Text, nullable=True)

    person_id = Column(Integer, ForeignKey("people.id"))
    person = relationship("Person", back_populates="aliyot")

class Relationship(Base):
    __tablename__ = "relationships"
    id = Column(Integer, primary_key=True, index=True)
    relation_type = Column(String, nullable=False)

    person_id = Column(Integer, ForeignKey("people.id"))
    related_person_id = Column(Integer, ForeignKey("people.id"))

    person = relationship("Person", foreign_keys=[person_id], backref="outgoing_relations")
    related_person = relationship("Person", foreign_keys=[related_person_id], backref="incoming_relations")
