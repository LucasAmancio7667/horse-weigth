import pytest
from sqlalchemy.exc import IntegrityError

from app.models import (
    Animal,
    EstimateMethod,
    Landmark,
    LandmarkName,
    Measurement,
    Photo,
    WeightEstimate,
)


def make_chain(session):
    animal = Animal(name="Estrela", breed="Quarto de Milha", withers_height_cm=148)
    photo = Photo(animal=animal, blob_name="estrela/2026-11-02.jpg", marker_size_cm=10, pixels_per_cm=20.5)
    photo.landmarks = [
        Landmark(name=LandmarkName.withers, x=410.5, y=120.0),
        Landmark(name=LandmarkName.buttock, x=1020.0, y=300.0),
    ]
    measurement = Measurement(photo=photo, body_length_cm=158.0, chest_height_cm=70.0, chest_girth_cm=185.0)
    measurement.estimates = [WeightEstimate(estimated_kg=480.0, method=EstimateMethod.formula)]
    session.add(animal)
    session.commit()
    return animal, photo, measurement


def test_full_chain_is_persisted(session):
    animal, photo, measurement = make_chain(session)

    loaded = session.get(Animal, animal.id)
    assert loaded.photos[0].landmarks[0].name == LandmarkName.withers
    assert loaded.photos[0].measurements[0].estimates[0].estimated_kg == 480.0
    # peso real da balança é opcional
    assert loaded.photos[0].actual_weight_kg is None


def test_deleting_animal_cascades_to_everything(session):
    animal, *_ = make_chain(session)
    session.delete(animal)
    session.commit()

    for model in (Photo, Landmark, Measurement, WeightEstimate):
        assert session.query(model).count() == 0


def test_same_landmark_cannot_repeat_in_one_photo(session):
    animal, photo, _ = make_chain(session)
    session.add(Landmark(photo_id=photo.id, name=LandmarkName.withers, x=1, y=1))
    with pytest.raises(IntegrityError):
        session.commit()


def test_photo_requires_existing_animal(session):
    session.add(Photo(animal_id=999, blob_name="x.jpg"))
    with pytest.raises(IntegrityError):
        session.commit()
