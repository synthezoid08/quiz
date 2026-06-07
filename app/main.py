from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    from app.db.session import engine
    import app.db.base  # noqa: F401
    from app.db.base_class import Base
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Welcome to AdaptQuiz API"}


app.include_router(
    auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"]
)

from app.api import notes, quiz
app.include_router(
    notes.router, prefix=f"{settings.API_V1_STR}/notes", tags=["notes"]
)
app.include_router(
    quiz.router, prefix=f"{settings.API_V1_STR}/quiz", tags=["quiz"]
)
