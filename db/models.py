from datetime import datetime
from typing import List
from sqlalchemy import String, ForeignKey, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from db.schemas import StatusEnum, AdminRole

from db.database import Base

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    fullname: Mapped[str] = mapped_column(String(50), nullable=False)
    hashed_password: Mapped[str]
    role: Mapped[AdminRole]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class POS_Agents(Base):
    __tablename__ = 'pos_agents'
    id: Mapped[int] = mapped_column(primary_key=True)
    terminal_id: Mapped[str] = mapped_column(unique=True)
    account_number: Mapped[str] = mapped_column(String(10), unique=True)
    agent_name: Mapped[str]
    transactions: Mapped[List["Transactions"]] = relationship( back_populates="pos_agent", cascade="all, delete-orphan")

class Transactions(Base):
    __tablename__ = 'transactions'
    id: Mapped[int] = mapped_column(primary_key=True)
    retrieval_ref: Mapped[str] = mapped_column(nullable=False)
    amount: Mapped[float]
    reference: Mapped[str]
    status: Mapped[StatusEnum] = mapped_column(default=StatusEnum.notAvailable)
    pos_id: Mapped[int] = mapped_column(ForeignKey("pos_agents.id"))
    pos_agent: Mapped["POS_Agents"] = relationship(back_populates="transactions")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

