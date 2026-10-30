"""Modelo de dados do app.

Fluxo: Animal -> Photo -> Landmark (pontos marcados) -> Measurement (cm) -> WeightEstimate (kg).
O peso real da balança é opcional e fica na Photo, para a coleta futura entrar sem mudar o esquema.
"""

import enum
from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Sex(str, enum.Enum):
    male = "male"
    female = "female"
    gelding = "gelding"  # castrado


class LandmarkName(str, enum.Enum):
    withers = "withers"  # cernelha
    shoulder = "shoulder"  # ponta do ombro
    buttock = "buttock"  # ponta da nádega
    chest_bottom = "chest_bottom"  # linha inferior do tórax
    hoof = "hoof"  # casco


class LandmarkSource(str, enum.Enum):
    manual = "manual"
    auto = "auto"  # marcado pelo modelo de pose (Sprint 4)


class EstimateMethod(str, enum.Enum):
    formula = "formula"  # fórmula clássica
    regression = "regression"  # regressão treinada (fase futura)


class Animal(Base):
    __tablename__ = "animals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    breed: Mapped[str | None] = mapped_column(String(80))
    sex: Mapped[Sex | None] = mapped_column(Enum(Sex))
    birth_date: Mapped[date | None] = mapped_column(Date)
    is_pregnant: Mapped[bool] = mapped_column(Boolean, default=False)
    withers_height_cm: Mapped[float | None] = mapped_column(Float)  # escala alternativa ao marcador
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    photos: Mapped[list["Photo"]] = relationship(back_populates="animal", cascade="all, delete-orphan")


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    animal_id: Mapped[int] = mapped_column(ForeignKey("animals.id", ondelete="CASCADE"), index=True)
    blob_name: Mapped[str] = mapped_column(String(255), unique=True)  # caminho no Blob Storage
    taken_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    marker_size_cm: Mapped[float | None] = mapped_column(Float)  # lado do ArUco impresso
    pixels_per_cm: Mapped[float | None] = mapped_column(Float)  # escala calculada
    actual_weight_kg: Mapped[float | None] = mapped_column(Float)  # peso de balança, quando existir

    animal: Mapped[Animal] = relationship(back_populates="photos")
    landmarks: Mapped[list["Landmark"]] = relationship(back_populates="photo", cascade="all, delete-orphan")
    measurements: Mapped[list["Measurement"]] = relationship(back_populates="photo", cascade="all, delete-orphan")


class Landmark(Base):
    __tablename__ = "landmarks"
    __table_args__ = (UniqueConstraint("photo_id", "name", name="uq_landmark_photo_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    photo_id: Mapped[int] = mapped_column(ForeignKey("photos.id", ondelete="CASCADE"), index=True)
    name: Mapped[LandmarkName] = mapped_column(Enum(LandmarkName))
    x: Mapped[float] = mapped_column(Float)  # pixels
    y: Mapped[float] = mapped_column(Float)  # pixels
    source: Mapped[LandmarkSource] = mapped_column(Enum(LandmarkSource), default=LandmarkSource.manual)

    photo: Mapped[Photo] = relationship(back_populates="landmarks")


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    photo_id: Mapped[int] = mapped_column(ForeignKey("photos.id", ondelete="CASCADE"), index=True)
    body_length_cm: Mapped[float | None] = mapped_column(Float)
    chest_height_cm: Mapped[float | None] = mapped_column(Float)
    chest_girth_cm: Mapped[float | None] = mapped_column(Float)  # estimado, não medido
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    photo: Mapped[Photo] = relationship(back_populates="measurements")
    estimates: Mapped[list["WeightEstimate"]] = relationship(
        back_populates="measurement", cascade="all, delete-orphan"
    )


class WeightEstimate(Base):
    __tablename__ = "weight_estimates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    measurement_id: Mapped[int] = mapped_column(ForeignKey("measurements.id", ondelete="CASCADE"), index=True)
    estimated_kg: Mapped[float] = mapped_column(Float)
    method: Mapped[EstimateMethod] = mapped_column(Enum(EstimateMethod), default=EstimateMethod.formula)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    measurement: Mapped[Measurement] = relationship(back_populates="estimates")
