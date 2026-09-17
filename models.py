# str-api/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)  
    document_name = Column(String)
    status = Column(String, default="pending")  
    raw_text = Column(Text, nullable=True)  # 🚀 ADDED RAW TEXT STORAGE FIELD
    extracted_data = Column(Text, nullable=True) 
    created_at = Column(DateTime, server_default=func.now())