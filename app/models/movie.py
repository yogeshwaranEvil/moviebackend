# app/models/movie.py
from app.database import db

movie_collection = db["movies"]
watchlist_collection = db["watchlists"]