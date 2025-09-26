from fastapi import FastAPI, Depends, Form, Request, UploadFile, File
from fastapi.responses import RedirectResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import requests
import pandas as pd
import io
from . import models, schemas, crud, database

app = FastAPI()
models.Base.metadata.create_all(bind=database.engine)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# --- Home
@app.get("/")
def home(request: Request, db: Session = Depends(database.get_db)):
    people = crud.get_people(db)
    aliyot = crud.get_aliyot(db)
    return templates.TemplateResponse("index.html", {"request": request, "people": people, "aliyot": aliyot})

# --- People
@app.get("/people")
def list_people(request: Request, db: Session = Depends(database.get_db)):
    people = crud.get_people(db)
    return templates.TemplateResponse("people.html", {"request": request, "people": people})

@app.post("/people")
def add_person(
    first_name: str = Form(...),
    last_name: str = Form(None),
    hebrew_name: str = Form(None),
    father_hebrew_name: str = Form(None),
    tribe: str = Form("ישראל"),
    notes: str = Form(None),
    db: Session = Depends(database.get_db)
):
    person = schemas.PersonCreate(
        first_name=first_name,
        last_name=last_name,
        hebrew_name=hebrew_name,
        father_hebrew_name=father_hebrew_name,
        tribe=tribe,
        notes=notes
    )
    crud.create_person(db, person)
    return RedirectResponse(url="/people", status_code=303)

# --- Inline update People
@app.post("/update/person/{person_id}")
def update_person(
    person_id: int,
    field: str = Form(...),
    value: str = Form(...),
    db: Session = Depends(database.get_db)
):
    person = db.query(models.Person).get(person_id)
    if not person:
        return JSONResponse({"error": "Not found"}, status_code=404)
    setattr(person, field, value)
    db.commit()
    db.refresh(person)
    return {"status": "ok"}

# --- Import/Export People
@app.get("/export/people.csv")
def export_people_csv(db: Session = Depends(database.get_db)):
    people = crud.get_people(db)
    df = pd.DataFrame([{
        "id": p.id,
        "first_name": p.first_name,
        "last_name": p.last_name,
        "hebrew_name": p.hebrew_name,
        "father_hebrew_name": p.father_hebrew_name,
        "tribe": p.tribe,
        "notes": p.notes
    } for p in people])
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=people.csv"
    return response

@app.get("/export/people.xlsx")
def export_people_excel(db: Session = Depends(database.get_db)):
    people = crud.get_people(db)
    df = pd.DataFrame([{
        "id": p.id,
        "first_name": p.first_name,
        "last_name": p.last_name,
        "hebrew_name": p.hebrew_name,
        "father_hebrew_name": p.father_hebrew_name,
        "tribe": p.tribe,
        "notes": p.notes
    } for p in people])
    stream = io.BytesIO()
    with pd.ExcelWriter(stream, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="People")
    stream.seek(0)
    response = StreamingResponse(stream, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response.headers["Content-Disposition"] = "attachment; filename=people.xlsx"
    return response

@app.post("/import/people")
def import_people(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    if file.filename.endswith(".csv"):
        df = pd.read_csv(file.file)
    else:
        df = pd.read_excel(file.file)
    for _, row in df.iterrows():
        person = schemas.PersonCreate(
            first_name=row.get("first_name"),
            last_name=row.get("last_name"),
            hebrew_name=row.get("hebrew_name"),
            father_hebrew_name=row.get("father_hebrew_name"),
            tribe=row.get("tribe", "ישראל"),
            notes=row.get("notes")
        )
        crud.create_person(db, person)
    return RedirectResponse(url="/people", status_code=303)

# --- Aliyot
@app.get("/aliyot")
def list_aliyot(request: Request, db: Session = Depends(database.get_db)):
    aliyot = crud.get_aliyot(db)
    people = crud.get_people(db)
    return templates.TemplateResponse("aliyot.html", {"request": request, "aliyot": aliyot, "people": people})

@app.post("/aliyot")
def add_aliyah(
    date: str = Form(...),
    parsha: str = Form(""),
    yomtov: str = Form(""),
    service: str = Form(...),
    aliyah_number: str = Form(...),
    reason: str = Form(None),
    person_id: int = Form(...),
    db: Session = Depends(database.get_db)
):
    aliyah = schemas.AliyahCreate(
        date=date,
        parsha=parsha,
        yomtov=yomtov,
        service=service,
        aliyah_number=aliyah_number,
        reason=reason,
        person_id=person_id
    )
    crud.create_aliyah(db, aliyah)
    return RedirectResponse(url="/aliyot", status_code=303)

# --- Inline update Aliyot
@app.post("/update/aliyah/{aliyah_id}")
def update_aliyah(
    aliyah_id: int,
    field: str = Form(...),
    value: str = Form(...),
    db: Session = Depends(database.get_db)
):
    aliyah = db.query(models.Aliyah).get(aliyah_id)
    if not aliyah:
        return JSONResponse({"error": "Not found"}, status_code=404)
    setattr(aliyah, field, value)
    db.commit()
    db.refresh(aliyah)
    return {"status": "ok"}

# --- Import/Export Aliyot
@app.get("/export/aliyot.csv")
def export_aliyot_csv(db: Session = Depends(database.get_db)):
    aliyot = crud.get_aliyot(db)
    df = pd.DataFrame([{
        "id": a.id,
        "date": a.date,
        "parsha": a.parsha,
        "yomtov": a.yomtov,
        "service": a.service,
        "aliyah_number": a.aliyah_number,
        "reason": a.reason,
        "person": f"{a.person.hebrew_name or ''} בן {a.person.father_hebrew_name or ''}"
    } for a in aliyot])
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=aliyot.csv"
    return response

@app.get("/export/aliyot.xlsx")
def export_aliyot_excel(db: Session = Depends(database.get_db)):
    aliyot = crud.get_aliyot(db)
    df = pd.DataFrame([{
        "id": a.id,
        "date": a.date,
        "parsha": a.parsha,
        "yomtov": a.yomtov,
        "service": a.service,
        "aliyah_number": a.aliyah_number,
        "reason": a.reason,
        "person": f"{a.person.hebrew_name or ''} בן {a.person.father_hebrew_name or ''}"
    } for a in aliyot])
    stream = io.BytesIO()
    with pd.ExcelWriter(stream, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Aliyot")
    stream.seek(0)
    response = StreamingResponse(stream, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response.headers["Content-Disposition"] = "attachment; filename=aliyot.xlsx"
    return response

# --- Hebcal API
@app.get("/api/parsha-yomtov")
def get_parsha_yomtov(date: str):
    """Return parsha (Hebrew), yomtov, and type of day"""
    try:
        leyning_url = f"https://www.hebcal.com/leyning?cfg=json&start={date}&end={date}"
        leyning_resp = requests.get(leyning_url)
        leyning_data = leyning_resp.json()

        parsha = ""
        yomtov = ""
        day_type = "weekday"

        for item in leyning_data.get("items", []):
            if "name" in item:
                if "he" in item["name"]:
                    parsha = item["name"]["he"]
                elif "en" in item["name"]:
                    parsha = item["name"]["en"]

            t = item.get("type")
            if t == "shabbat":
                day_type = "shabbat"
            elif t == "yomtov":
                yomtov = item["name"]["he"]
                day_type = "yomtov"
            elif t == "roshchodesh":
                yomtov = item["name"]["he"]
                day_type = "roshchodesh"
            elif t == "weekday":
                day_type = "weekday"

            if "name" in item and "he" in item["name"]:
                name_he = item["name"]["he"]
                if "כיפור" in name_he:
                    yomtov = name_he
                    day_type = "yomkippur"
                if "שמחת תורה" in name_he:
                    yomtov = name_he
                    day_type = "simchattorah"

        return JSONResponse({
            "parsha": parsha,
            "yomtov": yomtov,
            "day_type": day_type
        })
    except Exception as e:
        return JSONResponse({
            "parsha": "",
            "yomtov": "",
            "day_type": "weekday",
            "error": str(e)
        })
