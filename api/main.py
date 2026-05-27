from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.config import settings
from core.exceptions import AppException
from database.connection import init_pool, close_pool
from routes import operadores, ordens, coleta


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: inicializa o pool de conexões Oracle
    await init_pool()
    yield
    # Shutdown: fecha o pool
    await close_pool()


app = FastAPI(
    title="Pick By Voice API",
    description="Sistema de separação de pedidos por voz — Cardeal Distribuidora",
    version="1.0.0",
    lifespan=lifespan,
)


# Handler global: todas as AppException viram JSON com o status correto
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


# Registra as rotas com prefixo /api
app.include_router(operadores.router, prefix="/api")
app.include_router(ordens.router,     prefix="/api")
app.include_router(coleta.router,     prefix="/api")


@app.get("/api/status", tags=["Health"])
async def status():
    return {"status": "ok", "env": settings.API_ENV}
