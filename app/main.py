from fastapi import FastAPI, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from . import models, schemas, crud, database

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# --- Home ---
@app.get("/")
def home(request: Request, db: Session = Depends(database.get_db)):
    people = crud.get_people(db)
    aliyot = crud.get_aliyot(db)
    return templates.TemplateResponse("index.html", {"request": request, "people": people, "aliyot": aliyot})

# --- People ---
@app.get("/people")
def list_people(request: Request, db: Session = Depends(database.get_db)):
    people = crud.get_people(db)
    return templates.TemplateResponse("people.html", {"request": request, "people": people})

@app.post("/people")
def add_person(
    english_name: str = Form(...),
    hebrew_name: str = Form(None),
    notes: str = Form(None),
    db: Session = Depends(database.get_db)
):
    person = schemas.PersonCreate(english_name=english_name, hebrew_name=hebrew_name, notes=notes)
    crud.create_person(db, person)
    return RedirectResponse(url="/people", status_code=303)

# --- Aliyot ---
@app.get("/aliyot")
def list_aliyot(request: Request, db: Session = Depends(database.get_db)):
    aliyot = crud.get_aliyot(db)
    people = crud.get_people(db)
    return templates.TemplateResponse("aliyot.html", {"request": request, "aliyot": aliyot, "people": people})

@app.post("/aliyot")
def add_aliyah(
    date: str = Form(...),
    parsha: str = Form(...),
    service: str = Form(...),
    aliyah_number: str = Form(...),
    reason: str = Form(None),
    person_id: int = Form(...),
    db: Session = Depends(database.get_db)
):
    aliyah = schemas.AliyahCreate(date=date, parsha=parsha, service=service, aliyah_number=aliyah_number, reason=reason, person_id=person_id)
    crud.create_aliyah(db, aliyah)
    return RedirectResponse(url="/aliyot", status_code=303)

# --- Relationships ---
@app.get("/relationships")
def list_relationships(request: Request, db: Session = Depends(database.get_db)):
    relationships = crud.get_relationships(db)
    people = crud.get_people(db)
    return templates.TemplateResponse("relationships.html", {"request": request, "relationships": relationships, "people": people})

@app.post("/relationships")
def add_relationship(
    relation_type: str = Form(...),
    person_id: int = Form(...),
    related_person_id: int = Form(...),
    db: Session = Depends(database.get_db)
):
    rel = schemas.RelationshipCreate(relation_type=relation_type, person_id=person_id, related_person_id=related_person_id)
    crud.create_relationship(db, rel)
    return RedirectResponse(url="/relationships", status_code=303)
