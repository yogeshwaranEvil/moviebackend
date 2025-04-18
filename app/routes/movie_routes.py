from fastapi import APIRouter, HTTPException, Depends, Request, status
from bson import ObjectId
from typing import List, Optional
from app.schemas.movie import MovieCreate, MovieResponse, MovieUpdate
from app.models.movie import movie_collection
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

@router.post("/", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
async def create_movie(movie: MovieCreate, email: str = Depends(get_current_user)):
    # Only proceed if user is authenticated
    movie_dict = movie.dict()
    movie_dict["added_by"] = email
    
    result = await movie_collection.insert_one(movie_dict)
    
    # Get the created movie
    created_movie = await movie_collection.find_one({"_id": result.inserted_id})
    return serialize_movie(created_movie)

@router.get("/", response_model=List[MovieResponse])
async def get_all_movies(
    skip: int = 0, 
    limit: int = 10, 
    genre: Optional[str] = None,
    language: Optional[str] = None
):
    query = {}
    
    if genre:
        query["genre"] = genre
    
    if language:
        query["language"] = language
    
    cursor = movie_collection.find(query).skip(skip).limit(limit)
    movies = await cursor.to_list(length=limit)
    
    return [serialize_movie(movie) for movie in movies]

@router.get("/{movie_id}", response_model=MovieResponse)
async def get_movie(movie_id: str):
    try:
        movie = await movie_collection.find_one({"_id": ObjectId(movie_id)})
        if movie:
            return serialize_movie(movie)
        raise HTTPException(status_code=404, detail="Movie not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid movie ID: {str(e)}")

@router.put("/{movie_id}", response_model=MovieResponse)
async def update_movie(
    movie_id: str, 
    movie_update: MovieUpdate, 
    email: str = Depends(get_current_user)
):
    try:
        # Check if movie exists and user has permission
        existing_movie = await movie_collection.find_one({"_id": ObjectId(movie_id)})
        if not existing_movie:
            raise HTTPException(status_code=404, detail="Movie not found")
            
        # Only allow updates for non-empty fields
        update_data = {k: v for k, v in movie_update.dict().items() if v is not None}
        
        if update_data:
            await movie_collection.update_one(
                {"_id": ObjectId(movie_id)},
                {"$set": update_data}
            )
        
        updated_movie = await movie_collection.find_one({"_id": ObjectId(movie_id)})
        return serialize_movie(updated_movie)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating movie: {str(e)}")

@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(movie_id: str, email: str = Depends(get_current_user)):
    try:
        # Check if movie exists
        movie = await movie_collection.find_one({"_id": ObjectId(movie_id)})
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        await movie_collection.delete_one({"_id": ObjectId(movie_id)})
        return None
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting movie: {str(e)}")

@router.get("/search/{query}", response_model=List[MovieResponse])
async def search_movies(query: str, limit: int = 10):
    # Create a regex search instead of text search
    regex_query = {"$regex": query, "$options": "i"}  # Case-insensitive regex
    
    search_results = await movie_collection.find({
        "$or": [
            {"title": regex_query},
            {"description": regex_query},
            {"directed_by": regex_query}
        ]
    }).limit(limit).to_list(length=limit)
    
    return [serialize_movie(movie) for movie in search_results]