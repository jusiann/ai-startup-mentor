from sqlalchemy import String, DateTime, func, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.lib.db.database import Base
from datetime import datetime

class Idea(Base):
    __tablename__ = "ideas"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    session_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    executive_summary: Mapped[str] = mapped_column(Text, nullable=False)
    market_analysis: Mapped[str] = mapped_column(Text, nullable=False)
    swot_analysis: Mapped[str] = mapped_column(Text, nullable=False)
    business_model: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="ideas")
