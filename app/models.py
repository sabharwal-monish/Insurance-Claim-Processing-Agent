from sqlalchemy import Column, Integer, String, Text, DateTime
from app.db_helper import Base
import datetime

class InsuranceClaim(Base):
    __tablename__ = "insurance_claims"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True)
    policy_number = Column(String(50), nullable=True)
    vehicle_info = Column(String(255), nullable=True)
    incident_date = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    photo_url = Column(String(500), nullable=True)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)