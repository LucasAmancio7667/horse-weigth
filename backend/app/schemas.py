from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from .models import Sex


class AnimalCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    breed: str | None = Field(default=None, max_length=80)
    sex: Sex | None = None
    birth_date: date | None = None
    is_pregnant: bool = False
    withers_height_cm: float | None = Field(default=None, gt=0, lt=250)


class AnimalOut(AnimalCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
