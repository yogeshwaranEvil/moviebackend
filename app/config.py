import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "this is evil-dead")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_SECONDS = 3600  # 1 hour
