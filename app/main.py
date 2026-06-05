from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from app.database import get_db, engine
from app.models import Base, Question

app = FastAPI(title="Questions API", version="1.0.0")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


class QuestionCreate(BaseModel):
    question: str
    answer: str
    category: str | None = None
    source: str | None = None


@app.get("/")
def root():
    return {"message": "Questions API funcionando"}


@app.get("/questions")
def list_questions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Question).offset(skip).limit(limit).all()


@app.get("/questions/category/{category}")
def get_by_category(category: str, db: Session = Depends(get_db)):
    questions = (
        db.query(Question)
        .filter(func.lower(Question.category) == category.lower())
        .all()
    )
    if not questions:
        raise HTTPException(status_code=404, detail=f"No hay preguntas para '{category}'")
    return questions


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Question.id)).scalar()
    by_category = (
        db.query(Question.category, func.count(Question.id))
        .group_by(Question.category)
        .all()
    )
    return {
        "total": total,
        "by_category": {cat: count for cat, count in by_category},
    }


@app.get("/questions/{question_id}")
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    return question


@app.post("/questions", status_code=201)
def create_question(payload: QuestionCreate, db: Session = Depends(get_db)):
    question = Question(**payload.model_dump())
    db.add(question)
    db.commit()
    db.refresh(question)
    return question

@app.delete("/questions/{question_id}", status_code=204)
def delete_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    db.delete(question)
    db.commit()