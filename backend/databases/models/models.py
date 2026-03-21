from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from databases.config import Base
import datetime

class Merchant(Base):
    __tablename__ = "merchants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    category = Column(String) 
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    transactions = relationship("Transaction", back_populates="owner")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    merchant_id = Column(Integer, ForeignKey("merchants.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    owner = relationship("Merchant", back_populates="transactions")