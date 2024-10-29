import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
import uvicorn
from sqlalchemy.testing.plugin.plugin_base import logging
from fastapi.middleware.cors import CORSMiddleware

from ai_moderation_bot.data_models import UserCreate, UserLogin, UpdateSafetySetting
from ai_moderation_bot.db import get_api_session
from ai_moderation_bot.db_models import User, ContentAllowed, ContentBlocked
from ai_moderation_bot.services import (insert_into_db, encryption, add_safety_settings_to_db, update_safety_settings_in_db,
                                        get_latest_settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    add_safety_settings_to_db()
    get_latest_settings()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register")
async def register(user: UserCreate, session: Session = Depends(get_api_session)):
    db_user = session.query(User).filter(User.username == user.username).first()
    if db_user:
        logging.error(f"{user.username} already registered")
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = encryption(user.password)
    new_user = User(name=user.name, username=user.username, hashed_password=hashed_password, role=user.role)
    insert_into_db(new_user)
    return {"message": "User registered successfully"}


@app.post("/login")
async def login(user: UserLogin, session: Session = Depends(get_api_session)):
    hashed_password = encryption(user.password)
    db_user = session.query(User).filter(User.username == user.username, User.hashed_password == hashed_password).first()
    if not db_user:
        logging.error("Incorrect username or password")
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"username": db_user.username, "role": db_user.role}


@app.get("/content-stats")
async def get_content_stats(db: Session = Depends(get_api_session)):
    allowed_counts = db.query(
        ContentAllowed.tg_users_nickname,
        func.count(ContentAllowed.id).label('allowed_count')
    ).group_by(ContentAllowed.tg_users_nickname).all()

    blocked_counts = db.query(
        ContentBlocked.tg_users_nickname,
        func.count(ContentBlocked.id).label('blocked_count')
    ).group_by(ContentBlocked.tg_users_nickname).all()

    user_stats = {}

    for user, count in allowed_counts:
        if user not in user_stats:
            user_stats[user] = {"allowed_count": 0, "blocked_count": 0}
        user_stats[user]["allowed_count"] = count

    for user, count in blocked_counts:
        if user not in user_stats:
            user_stats[user] = {"allowed_count": 0, "blocked_count": 0}
        user_stats[user]["blocked_count"] = count

    return user_stats


@app.post('/update-safety-settings')
async def update_safe_settings(updated_settings: List[UpdateSafetySetting]):
    update_safety_settings_in_db(updated_settings)
    return  {"message": "Settings updated successfully"}


def main():
    uvicorn.run("ai_moderation_bot.api:app", host="127.0.0.1", port=8000, log_level="info", reload=True)


if __name__ == "__main__":
    main()