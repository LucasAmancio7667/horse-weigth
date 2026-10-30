from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from .. import storage
from ..db import get_db

router = APIRouter(tags=["saúde"])


@router.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        database = "ok"
    except Exception:
        database = "unavailable"

    blob = "ok" if storage.is_available() else "unavailable"
    # A API está de pé se o banco responde; o storage é reportado à parte.
    return {"status": "ok" if database == "ok" else "degraded", "database": database, "storage": blob}
