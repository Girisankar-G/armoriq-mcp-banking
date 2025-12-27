from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
# Use a relative import to find database.py in the same folder
from .database import Base

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_name = Column(String, unique=True, index=True)
    balance = Column(Float, default=0.0)
    
    # Relationship to the Transaction model
    transactions = relationship("Transaction", back_populates="owner")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    type = Column(String)  # DEPOSIT or WITHDRAWAL
    amount = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship back to the Account model
    owner = relationship("Account", back_populates="transactions")