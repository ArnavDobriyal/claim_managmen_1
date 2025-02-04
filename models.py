import uuid
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, Session
from database import Base, AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import Boolean

class Policyholder(Base):
    __tablename__ = "policyholders"
    
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False) 
    is_admin = Column(Boolean, default=False)  
    
    policies = relationship("Policy", back_populates="policyholder", cascade="all, delete")
    claims = relationship("Claim", back_populates="policyholder", cascade="all, delete")
    
    def set_admin_status(self):
        if self.password == "admin1234":
            self.is_admin = True
        else:
            self.is_admin = False



class Policy(Base):
    __tablename__ = "policies"
    policy_id = Column(Integer, primary_key=True)
    policyholder_id = Column(Integer, ForeignKey("policyholders.id"), nullable=False)
    coverage = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    
    policyholder = relationship("Policyholder", back_populates="policies")
    claims = relationship("Claim", back_populates="policy", cascade="all, delete")

class Claim(Base):
    __tablename__ = "claims"
    claim_id = Column(Integer, primary_key=True)
    policy_id = Column(Integer, ForeignKey("policies.policy_id"), nullable=False)
    policyholder_id = Column(Integer, ForeignKey("policyholders.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    
    policy = relationship("Policy", back_populates="claims")
    policyholder = relationship("Policyholder", back_populates="claims")
from sqlalchemy.exc import SQLAlchemyError 