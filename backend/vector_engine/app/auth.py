# app/auth.py
from fastapi import Header, HTTPException, Depends
from jose import jwt, JWTError
from app.config import settings

def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid format")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(401, "Missing user_id")
        return {"user_id": int(user_id)}
    except JWTError:
        raise HTTPException(401, "Invalid token")