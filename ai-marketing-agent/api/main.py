from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.session import init_db
from api.routes import campaigns_router, content_router, outreach_router
from utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database on startup."""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database ready.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="AI Marketing Automation System",
    description=(
        "Multi-agent marketing automation system using LangChain + OpenAI. "
        "Orchestrates campaign planning, content generation, and outreach execution end-to-end."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(campaigns_router)
app.include_router(content_router)
app.include_router(outreach_router)


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "AI Marketing Automation System",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}
