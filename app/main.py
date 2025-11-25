from fastapi import FastAPI, Depends, HTTPException
from . import crud, models, schemas
from .database import SessionLocal, engine, Base
from sqlalchemy.orm import Session


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Leads Distributor")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/operators/", response_model=schemas.OperatorOut)
def create_operator(oper: schemas.OperatorCreate, db: Session = Depends(get_db)):
    return crud.create_operator(db, oper)


@app.get("/operators/", response_model=list[schemas.OperatorOut])
def list_ops(db: Session = Depends(get_db)):
    return crud.list_operators(db)


@app.patch("/operators/{operator_id}", response_model=schemas.OperatorOut)
def patch_operator(operator_id, oper: schemas.OperatorCreate, db: Session = Depends(get_db)):
    update = crud.update_operator(db, operator_id, active=oper.active, limit=oper.limit)
    if not update:
        raise HTTPException(status_code=404, detail="Operator not found")
    return update


@app.post("/sources/", response_model=schemas.SourceOut)
def create_source(source: schemas.SourceCreate, db: Session = Depends(get_db)):
    return crud.create_source(db, source)


@app.post("/sources/{source_id}/operators/")
def assign_operator(source_id: int, assign: schemas.SourceOperatorAssign, db: Session = Depends(get_db)):
    source_oper = crud.assign_operator_to_source(db, source_id, assign)
    if not source_oper:
        raise HTTPException(status_code=404, detail="Operator or Source not found")
    return {"id": source_oper.id, "source_id": source_oper.source_id, "operator_id": source_oper.operator_id, "weight": source_oper.weight}


@app.post("/contacts/", response_model=schemas.ContactOut)
def register_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    source = db.query(models.Source).filter(models.Source.id == contact.source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    res_contact = crud.create_contact(db, contact)
    return res_contact


@app.get("/leads/", response_model=list[schemas.LeadOut])
def list_leads(db: Session = Depends(get_db)):
    return crud.list_leads(db)


@app.get("/stats/")
def get_stats(db: Session = Depends(get_db)):
    return crud.stats(db)
