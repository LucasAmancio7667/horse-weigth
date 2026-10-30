from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models  # noqa: F401  (registra as tabelas no Base)
from .config import settings
from .db import Base, engine
from .routers import animals, health


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Sprint 1: cria as tabelas direto. Se o esquema começar a mudar, trocar por Alembic.
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="API de Peso de Cavalos", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = APIRouter(prefix="/api")
api.include_router(health.router)
api.include_router(animals.router)
app.include_router(api)
