from sqlalchemy import String, DateTime, func, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.lib.db.database import Base
from datetime import datetime

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    session_id: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    sender: Mapped[str] = mapped_column(String(50), nullable=False) # 'user' or 'ai'
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="chat_history")
