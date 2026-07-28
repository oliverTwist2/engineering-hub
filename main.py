from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.routes import router
from storage.metadata_db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application lifecycle startup and shutdown events.
    
    Parameters:
        app: Active FastAPI application instance.
    Returns: Async context manager lifecycle wrapper.
    """
    init_db()
    yield

app = FastAPI(
    title="Engineering Intelligence Hub",
    description="Developer-focused RAG system ingesting tech docs, code, and architecture diagrams.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
