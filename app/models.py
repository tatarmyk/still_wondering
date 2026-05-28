import hashlib
from datetime import datetime, timezone

from flask import Flask
from flask_login import UserMixin
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

engine = None
SessionLocal = None


class Base(DeclarativeBase):
    pass


class Author(Base, UserMixin):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)


class Essay(Base):
    __tablename__ = "essays"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    body_md = Column(Text, nullable=False, default="")
    published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
    eye_count = Column(Integer, default=0)


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    essay_id = Column(Integer, nullable=False, index=True)
    section_id = Column(String(100), nullable=False)
    author_name = Column(String(80), default="")
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ip_hash = Column(String(64), nullable=False)


def hash_ip(ip: str) -> str:
    """Hash an IP address for storage (no raw PII)."""
    return hashlib.sha256(ip.encode()).hexdigest()


def init_db(app: Flask):
    global engine, SessionLocal
    db_url = app.config["SQLALCHEMY_DATABASE_URI"]
    engine = create_engine(db_url, echo=False)
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)


def get_db() -> Session:
    """Get a new database session. Caller must close it."""
    return SessionLocal()
