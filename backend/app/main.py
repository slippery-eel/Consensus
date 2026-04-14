from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import analysis, participants, responses, settings, statements, summaries, surveys


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Consensus", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(surveys.router, prefix="/api")
app.include_router(statements.router, prefix="/api")
app.include_router(participants.router, prefix="/api")
app.include_router(responses.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(summaries.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
