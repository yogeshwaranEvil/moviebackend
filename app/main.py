from fastapi import FastAPI
from app.routes import auth_routes, movie_routes, watchlist_routes
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(title="Netflix Clone API", description="API for Netflix Clone application")

# Allow CORS from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can change this to your frontend domain later
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
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
# Text search index setup
# Text search index setup
@app.on_event("startup")
async def startup_db_client():
    from app.database import db
    
    try:
        # Drop existing text indexes first
        await db.movies.drop_indexes()
    except Exception:
        # Index might not exist, which is fine
        pass
    
    # Create new text index with explicit language_override that doesn't conflict
    await db.movies.create_index(
        [
            ("title", "text"),
            ("description", "text"),
            ("directed_by", "text")
        ],
        language_override="lang_override"  # Using a field that doesn't exist in your docs
    )
    
    # Create regular indexes for filtering
    await db.movies.create_index("language")
    await db.movies.create_index("genre")