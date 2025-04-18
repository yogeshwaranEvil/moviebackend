from fastapi import APIRouter, HTTPException, Depends, Request, status
from bson import ObjectId
from typing import List
from datetime import datetime
from app.schemas.movie import MovieResponse
from app.models.movie import movie_collection, watchlist_collection
from app.services.jwt_handler import decode_token


router = APIRouter()

# Helper function to authenticate users
async def get_current_user(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = auth.split(" ")[1]
    try:
        payload = decode_token(token)
        return payload["sub"]  # Return the user's email
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# Convert MongoDB _id to string
def serialize_movie(movie):
    movie["id"] = str(movie["_id"])
    del movie["_id"]
    return movie

@router.post("/{movie_id}", status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(movie_id: str, email: str = Depends(get_current_user)):
    try:
        # Check if movie exists
        movie = await movie_collection.find_one({"_id": ObjectId(movie_id)})
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        # Check if already in watchlist
        existing_entry = await watchlist_collection.find_one({
            "user_email": email,
            "movie_id": ObjectId(movie_id)
        })
        
        if existing_entry:
            raise HTTPException(status_code=400, detail="Movie already in watchlist")
        
        # Add to watchlist
        await watchlist_collection.insert_one({
            "user_email": email,
            "movie_id": ObjectId(movie_id),
            "added_at": datetime.utcnow()
        })
        
        return {"message": "Movie added to watchlist"}
    except Exception as e:
        if "Movie already in watchlist" in str(e) or "Movie not found" in str(e):
            raise e
        raise HTTPException(status_code=400, detail=f"Error adding to watchlist: {str(e)}")

@router.get("/", response_model=List[MovieResponse])
async def get_watchlist(email: str = Depends(get_current_user)):
    # Get all movie IDs in the user's watchlist
    watchlist_items = await watchlist_collection.find({"user_email": email}).to_list(length=100)
    
    if not watchlist_items:
        return []
    
    # Extract movie IDs
    movie_ids = [item["movie_id"] for item in watchlist_items]
    
    # Fetch all movies in the watchlist
    watchlist_movies = await movie_collection.find({"_id": {"$in": movie_ids}}).to_list(length=100)
    
    return [serialize_movie(movie) for movie in watchlist_movies]

@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_watchlist(movie_id: str, email: str = Depends(get_current_user)):
    try:
        # Remove from watchlist
        result = await watchlist_collection.delete_one({
            "user_email": email,
            "movie_id": ObjectId(movie_id)
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Movie not found in watchlist")
        
        return None
    except Exception as e:
        if "Movie not found in watchlist" in str(e):
            raise e
        raise HTTPException(status_code=400, detail=f"Error removing from watchlist: {str(e)}")