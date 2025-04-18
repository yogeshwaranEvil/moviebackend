from fastapi import FastAPI
from app.routes import auth_routes, movie_routes, watchlist_routes
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from mangum import Mangum

app = FastAPI(title="Netflix Clone API", description="API for Netflix Clone application")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(movie_routes.router, prefix="/movies", tags=["Movies"])
app.include_router(watchlist_routes.router, prefix="/watchlist", tags=["Watchlist"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Netflix Clone API",
        "docs": "/docs",
        "version": "1.0.0",
        "timestamp": datetime.utcnow()
    }

@app.on_event("startup")
async def startup_db_client():
    from app.database import db

    try:
        await db.movies.drop_indexes()
    except Exception:
        pass
    
    await db.movies.create_index(
        [
            ("title", "text"),
            ("description", "text"),
            ("directed_by", "text")
        ],
        language_override="lang_override"
    )
    await db.movies.create_index("language")
    await db.movies.create_index("genre")

# Vercel handler
handler = Mangum(app)
