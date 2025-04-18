# app/schemas/movie.py
from typing import List, Optional
from pydantic import BaseModel

class MovieCreate(BaseModel):
    title: str
    year: str
    imdb: str
    movie: str
    trailer: str
    poster: str
    description: str
    language: str
    genre: List[str]
    directed_by: str

class MovieResponse(BaseModel):
    id: str
    title: str
    year: str
    imdb: str
    movie: str
    trailer: str
    poster: str
    description: str
    language: str
    genre: List[str]
    directed_by: str

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    year: Optional[str] = None
    imdb: Optional[str] = None
    movie: Optional[str] = None
    trailer: Optional[str] = None
    poster: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None
    genre: Optional[List[str]] = None
    directed_by: Optional[str] = None