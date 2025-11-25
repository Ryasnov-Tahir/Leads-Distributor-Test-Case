"""Pydantic-схемы."""

from pydantic import BaseModel
from typing import Optional


class OperatorCreate(BaseModel):
    """
    Схема для создания нового оператора.

    :param name: Имя оператора.
    :param active: Флаг активности оператора.
    :param limit: Максимум обращений, которые может обрабатывать оператор.
    """

    name: str
    active: Optional[bool] = True
    limit: Optional[int] = 5


class OperatorOut(BaseModel):
    """
    Схема для вывода данных оператора.

    :ivar id: ID оператора.
    :ivar name: Имя оператора.
    :ivar active: Флаг активности оператора.
    :ivar limit: Максимум обращений, которые может обрабатывать оператор.
    """

    id: int
    name: str
    active: bool
    limit: int

    class Config:
        """Конфигурация Pydantic."""

        orm_mode = True


class SourceCreate(BaseModel):
    """
    Схема для создания нового источника.

    :param name: Название источника.
    """

    name: str


class SourceOut(BaseModel):
    """
    Схема для вывода информации об источнике.

    :ivar id: ID источника.
    :ivar name: Название источника.
    """

    id: int
    name: str

    class Config:
        """Конфигурация Pydantic."""

        orm_mode = True


class SourceOperatorAssign(BaseModel):
    """
    Модель для назначения оператора на источник.

    :ivar operator_id: ID оператора.
    :ivar weight: Нагрузка оператора для распределения по источнику.
    """

    operator_id: int
    weight: int = 1


class ContactCreate(BaseModel):
    """
    Схема для создания нового контакта.

    :param external_id: Внешний ID лида.
    :param e_mail: Email лида.
    :param source_id: ID источника.
    :param payload: Дополнительные данные контакта.
    """

    external_id: Optional[str] = None
    e_mail: Optional[str] = None
    source_id: int
    payload: Optional[str] = None


class ContactOut(BaseModel):
    """
    Схема вывода информации о контакте.

    :ivar id: ID контакта.
    :ivar lead_id: ID лида.
    :ivar source_id: ID источника.
    :ivar operator_id: ID оператора.
    :ivar status: Статус обращения.
    :ivar payload: Дополнительные данные контакта.
    """

    id: int
    lead_id: int
    source_id: int
    operator_id: Optional[int] = None
    status: str
    payload: Optional[str] = None

    class Config:
        """Конфигурация Pydantic."""

        orm_mode = True


class LeadOut(BaseModel):
    """
    Схема для вывода информации о лиде.

    :ivar id: ID лида.
    :ivar external_id: Внешний ID лида.
    :ivar e_mail: E-mail лида.
    """

    id: int
    external_id: Optional[str] = None
    e_mail: Optional[str] = None

    class Config:
        """Конфигурация Pydantic."""

        orm_mode = True
