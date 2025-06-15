# server.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# Database setup
DATABASE_URL = "sqlite:///./words.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Database model
class Word(Base):
    __tablename__ = "words"
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, unique=True, index=True)
    translation = Column(String)

Base.metadata.create_all(bind=engine)

# API setup
app = FastAPI()

# Request body model
class WordRequest(BaseModel):
    word: str

# API Endpoints
@app.post("/add-word")
def add_word(item: WordRequest):
    db = SessionLocal()
    existing = db.query(Word).filter(Word.word == item.word).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="Word already exists.")

    # For now, simple "fake translation"
    translation = item.word + "_translated"

    new_word = Word(word=item.word, translation=translation)
    db.add(new_word)
    db.commit()
    db.refresh(new_word)
    db.close()
    return {"id": new_word.id, "word": new_word.word, "translation": new_word.translation}

@app.get("/words")
def list_words():
    db = SessionLocal()
    words = db.query(Word).all()
    db.close()
    return [{"id": w.id, "word": w.word, "translation": w.translation} for w in words]

@app.delete("/delete-word/{word_id}")
def delete_word(word_id: int):
    db = SessionLocal()
    word = db.query(Word).filter(Word.id == word_id).first()
    if not word:
        db.close()
        raise HTTPException(status_code=404, detail="Word not found.")
    db.delete(word)
    db.commit()
    db.close()
    return {"detail": "Word deleted."}
