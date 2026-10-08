from pwdlib import PasswordHash
import os
import jwt
from dotenv import load_dotenv

load_dotenv()

password_hash = PasswordHash.recommended()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def create_access_token(data: dict):
    return jwt.encode(
        data,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )