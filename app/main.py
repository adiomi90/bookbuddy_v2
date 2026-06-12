from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routers import users, posts, comments
from app.database.deps import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: runs before the app starts handling requests
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: runs after the app stops (optional, e.g., dispose engine)
    await engine.dispose()

app = FastAPI(lifespan=lifespan, docs_url="/docs", redoc_url="/redoc")

@app.get("/")
async def root():
    return {"message": "Welcome to BookBuddy API"}

app.include_router(users.router, prefix="/users", tags=["users"] )
app.include_router(posts.router, prefix="/posts", tags=["posts"] )
app.include_router(comments.router, prefix="/comments", tags=["comments"] )
