from fastapi import APIRouter, Depends, Query
from typing import List
from sqlmodel import Session, select
from src.api.words.models import WordModel  # you’ll define this
from src.db.session import get_session  # your db session function

router = APIRouter()


@router.get("/", response_model=List[WordModel])
def get_words(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
):
    query = select(WordModel).offset(offset).limit(limit)
    results = session.exec(query).all()
    return results
