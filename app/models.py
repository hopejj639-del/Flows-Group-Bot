# Filename: app/models.py
from sqlalchemy import Column, BigInteger, String, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database import Base

class Group(Base):
    __tablename__ = "groups"

    # Telegram Group IDs can be negative and very large, BigInteger is mandatory.
    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    welcome_message = Column(Text, nullable=True)
    rules_text = Column(Text, nullable=True)

    # Relationships
    warnings = relationship("Warning", back_populates="group", cascade="all, delete-orphan")
    filters = relationship("Filter", back_populates="group", cascade="all, delete-orphan")

class Warning(Base):
    __tablename__ = "warnings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    group_id = Column(BigInteger, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    reason = Column(String(255), nullable=True)

    group = relationship("Group", back_populates="warnings")

class Filter(Base):
    __tablename__ = "filters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(BigInteger, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    keyword = Column(String(255), nullable=False, index=True)
    reply_text = Column(Text, nullable=False)

    group = relationship("Group", back_populates="filters")