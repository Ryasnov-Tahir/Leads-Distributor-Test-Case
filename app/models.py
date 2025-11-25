from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Text,
    Enum,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from .database import Base
import enum


class ContactStatus(str, enum.Enum):
    open = "open"
    closed = "closed"


class Operator(Base):
    __tablename__ = "operators"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    active = Column(Boolean, default=True)
    limit = Column(Integer, default=5)

    sources = relationship("SourceOperator", back_populates="operator")
    contacts = relationship("Contact", back_populates="operator")


class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    operators = relationship("SourceOperator", back_populates="source")
    contacts = relationship("Contact", back_populates="source")


class SourceOperator(Base):
    __tablename__ = "source_operators"
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    operator_id = Column(Integer, ForeignKey("operators.id"))
    weight = Column(Integer, nullable=False, default=10)

    source = relationship("Source", back_populates="operators")
    operator = relationship("Operator", back_populates="sources")

    __table_args__ = (
        UniqueConstraint("source_id", "operator_id", name="_source_operator_uc"),
    )


class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True)
    external_id = Column(String, nullable=True, index=True)
    e_mail = Column(String, nullable=True, index=True)

    contacts = relationship("Contact", back_populates="lead")


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    status = Column(Enum(ContactStatus), default=ContactStatus.open)
    payload = Column(Text, nullable=True)

    lead = relationship("Lead", back_populates="contacts")
    source = relationship("Source", back_populates="contacts")
    operator = relationship("Operator", back_populates="contacts")
