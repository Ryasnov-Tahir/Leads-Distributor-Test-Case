"""SQLAlchemy модели."""

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
from app.database import Base
import enum


CONTACTS_RELATION = "contacts"


class ContactStatus(str, enum.Enum):
    """
    Enum для статусов обращения.

    :cvar open: Статус "открыто".
    :cvar closed: Статус "закрыто".
    """

    open = "open"
    closed = "closed"


class Operator(Base):
    """
    Модель оператора.

    :ivar id: ID оператора.
    :ivar name: Имя оператора.
    :ivar active: Флаг активности оператора.
    :ivar limit: Максимум обращений, которые может обрабатывать оператор.
    :ivar sources: Связь с объектами SourceOperator.
    :ivar contacts: Связь с объектами Contact.
    """

    __tablename__ = "operators"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    active = Column(Boolean, default=True)
    limit = Column(Integer, default=5)

    sources = relationship("SourceOperator", back_populates="operator")
    contacts = relationship("Contact", back_populates="operator")


class Source(Base):
    """
    Модель источника.

    :ivar id: ID источника.
    :ivar name: Название источника.
    :ivar operators: Связь с объектами SourceOperator.
    :ivar contacts: Связь с объектами Contact.
    """

    __tablename__ = "sources"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    operators = relationship("SourceOperator", back_populates="source")
    contacts = relationship("Contact", back_populates="source")


class SourceOperator(Base):
    """
    Модель связи источников с операторами.

    :ivar id: ID связи.
    :ivar source_id: ID источника.
    :ivar operator_id: ID оператора.
    :ivar weight: Нагрузка оператора на данного источника.
    :ivar source: Связь с объектом Source.
    :ivar operator: Связь с объектом Operator.
    """

    __tablename__ = "source_operators"
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    operator_id = Column(Integer, ForeignKey("operators.id"))
    weight = Column(Integer, nullable=False, default=10)

    source = relationship("Source", back_populates="operators")
    operator = relationship("Operator", back_populates="sources")

    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "operator_id",
            name="_source_operator_uc"
        ),
    )


class Lead(Base):
    """
    Модель лида.

    :ivar id: ID лида.
    :ivar external_id: Внешний ID лида.
    :ivar e_mail: Email лида.
    :ivar contacts: Связь с объектами Contact.
    """

    __tablename__ = "leads"
    id = Column(Integer, primary_key=True)
    external_id = Column(String, nullable=True, index=True)
    e_mail = Column(String, nullable=True, index=True)

    contacts = relationship("Contact", back_populates="lead")


class Contact(Base):
    """
    Модель контакта лида через источник.

    :ivar id: ID контакта.
    :ivar lead_id: ID лида.
    :ivar source_id: ID источника.
    :ivar operator_id: ID оператора.
    :ivar status: Статус обращения.
    :ivar payload: Дополнительные данные контакта.
    :ivar lead: Связь с объектом Lead.
    :ivar source: Связь с объектом Source.
    :ivar operator: Связь с объектом Operator.
    """

    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id"))
    source_id = Column(Integer, ForeignKey("sources.id"))
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=True)
    status = Column(Enum(ContactStatus), default=ContactStatus.open)
    payload = Column(Text, nullable=True)

    lead = relationship("Lead", back_populates=CONTACTS_RELATION)
    source = relationship("Source", back_populates=CONTACTS_RELATION)
    operator = relationship("Operator", back_populates=CONTACTS_RELATION)
