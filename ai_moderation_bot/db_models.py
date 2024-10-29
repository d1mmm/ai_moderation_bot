from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from ai_moderation_bot.db import Base, engine
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now())


class TgUsers(Base):
    __tablename__ = "tg_users"

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, nullable=False, unique=True, index=True)


class ContentAllowed(Base):
    __tablename__ = "content_allowed"

    id = Column(Integer, primary_key=True)
    tg_users_nickname = Column(String, ForeignKey("tg_users.nickname"))
    text = Column(String, nullable=False)


class ContentBlocked(Base):
    __tablename__ = "content_blocked"

    id = Column(Integer, primary_key=True)
    tg_users_nickname = Column(String, ForeignKey("tg_users.nickname"))
    text = Column(String, nullable=False)


class SafetySetting(Base):
    __tablename__ = "safety_settings"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    method = Column(String, nullable=False)
    threshold = Column(String, nullable=False)


Base.metadata.create_all(bind=engine)
