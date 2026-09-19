from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    stripe_customer_id = Column(String(255), nullable=True) # 💳 Tracks them in Stripe's system
    is_active_subscriber = Column(Boolean, default=False) # 🔒 Subscription wall toggle flag
    created_at = Column(DateTime, server_default=func.now())

    # Establish link showing a user can own multiple analysis records
    jobs = relationship("AnalysisJob", back_populates="owner")


class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)  
    document_name = Column(String)
    status = Column(String, default="pending")  
    raw_text = Column(Text, nullable=True)  
    extracted_data = Column(Text, nullable=True) 
    created_at = Column(DateTime, server_default=func.now())

    # Establish backward link to the user profile
    owner = relationship("User", back_populates="jobs")