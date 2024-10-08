import os
import pytest
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Define the path to the database file
DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'db/lascaux.db'))
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    # Create a new database session for a test
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative class definitions
Base = declarative_base()

# Define your models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True)
    bio = Column(Text)
    created_at = Column(TIMESTAMP)
    profile_picture_url = Column(String)
    last_login = Column(TIMESTAMP)

    posts = relationship("Post", back_populates="owner")
    comments = relationship("Comment", back_populates="author")
    votes = relationship("Vote", back_populates="voter")

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    is_flagged = Column(Boolean, default=False)
    ipfs_hash = Column(String)

    owner = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    votes = relationship("Vote", back_populates="post")

class Vote(Base):
    __tablename__ = 'votes'
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    vote_value = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP)

    post = relationship("Post", back_populates="votes")
    voter = relationship("User", back_populates="votes")

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    comment_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP)
    parent_comment_id = Column(Integer, ForeignKey('comments.id'))

    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")

class ModerationLog(Base):
    __tablename__ = 'moderation_logs'
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    reason = Column(Text, nullable=False)
    flagged_by_ai = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP)