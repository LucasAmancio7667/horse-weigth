from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Animal
from ..schemas import AnimalCreate, AnimalOut

router = APIRouter(prefix="/animals", tags=["animais"])


@router.post("", response_model=AnimalOut, status_code=201)
def create_animal(payload: AnimalCreate, db: Session = Depends(get_db)):
    animal = Animal(**payload.model_dump())
    db.add(animal)
    db.commit()
    db.refresh(animal)
    return animal


@router.get("", response_model=list[AnimalOut])
def list_animals(db: Session = Depends(get_db)):
    return db.scalars(select(Animal).order_by(Animal.name)).all()


@router.get("/{animal_id}", response_model=AnimalOut)
def get_animal(animal_id: int, db: Session = Depends(get_db)):
    animal = db.get(Animal, animal_id)
    if animal is None:
        raise HTTPException(status_code=404, detail="Animal não encontrado")
    return animal
