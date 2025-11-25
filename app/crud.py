"""Бизнес-логика и операции с базой данных."""

from sqlalchemy.orm import Session
from app.models import (
    Operator,
    Source,
    SourceOperator,
    Lead,
    Contact,
    ContactStatus
)
from app.schemas import (
    OperatorCreate,
    SourceCreate,
    SourceOperatorAssign,
    ContactCreate
)
import random


def get_operator(session: Session, operator_id: int) -> Operator | None:
    """
    Получает оператора по его ID.

    :param session: Сессия для работы с базой данных.
    :param operator_id: ID оператора.
    :return: Объект operator или None.
    """
    return session.query(Operator).filter(Operator.id == operator_id).first()


def create_operator(session: Session, oper: OperatorCreate) -> Operator:
    """
    Создаёт нового оператора.

    :param session: Сессия для работы с базой данных.
    :param oper: Схема данных оператора.
    :return: Объект Operator.
    """
    db_oper = Operator(name=oper.name, active=oper.active, limit=oper.limit)
    session.add(db_oper)
    session.commit()
    session.refresh(db_oper)
    return db_oper


def get_opers_list(session: Session) -> list:
    """
    Получает список всех операторов из базы данных.

    :param session: Сессия SQLAlchemy для работы с базой данных.
    :return: Список объектов Operator.
    """
    return session.query(Operator).all()


def update_operator(
        session: Session,
        operator_id: int,
        active: bool | None = None,
        limit: int | None = None
) -> Operator | None:
    """
    Обновляет статус активности и/или лимит нагрузки оператора.

    :param session: Сессия для работы с базой данных.
    :param operator_id: ID оператора.
    :param active: Новый статус активности оператора.
    :param limit: Новый лимит количества активных обращений.
    :return: Объект Operator, либо None.
    """
    oper = get_operator(session, operator_id)
    if not oper:
        return None
    if active is not None:
        oper.active = active
    if limit is not None:
        oper.limit = limit
    session.commit()
    session.refresh(oper)
    return oper


def create_source(session: Session, source_create: SourceCreate) -> Source:
    """
    Создаёт новый источник.

    :param session: Сессия для работы с базой данных.
    :param source_create: Схема данных источника.
    :return: Объект Source.
    """
    source = Source(name=source_create.name)
    session.add(source)
    session.commit()
    session.refresh(source)
    return source


def assign_operator_to_source(
        session: Session,
        source_id: int,
        assign: SourceOperatorAssign
) -> SourceOperator | None:
    """
    Назначает оператора на источник.

    :param session: Сессия для работы с базой данных.
    :param source_id: ID источника.
    :param assign: Схема с ID и нагрузкой оператора.
    :return: Объект SourceOperator или None.
    """
    oper = get_operator(session, assign.operator_id)
    source = session.query(Source).filter(Source.id == source_id).first()
    if not oper or not source:
        return None
    source_oper = (
        session.query(SourceOperator)
        .filter_by(source_id=source_id, operator_id=assign.operator_id)
        .first()
    )
    if source_oper:
        source_oper.weight = assign.weight
    else:
        source_oper = SourceOperator(
            source_id=source_id,
            operator_id=assign.operator_id,
            weight=assign.weight
        )
        session.add(source_oper)
    session.commit()
    session.refresh(source_oper)
    return source_oper


def find_or_create_lead(
        session: Session,
        external_id: str | None = None,
        e_mail: str | None = None
) -> Lead:
    """
    Находит существующего лида либо создаёт нового.

    :param session: Сессия для работы с базой данных.
    :param external_id: ID лида.
    :param e_mail: E-mail лида.
    :return: Объект Lead.
    """
    query = session.query(Lead)
    if external_id:
        lead = query.filter(Lead.external_id == external_id).first()
        if lead:
            return lead
    if e_mail:
        lead = query.filter(Lead.e_mail == e_mail).first()
        if lead:
            return lead
    lead = Lead(external_id=external_id, e_mail=e_mail)
    session.add(lead)
    session.commit()
    session.refresh(lead)
    return lead


def count_active_contacts_for_operator(
        session: Session,
        operator_id: int
) -> int:
    """
    Подсчитывает количество обращений оператора.

    :param session: Сессия для работы с базой данных.
    :param operator_id: ID оператора.
    :return: Количество обращений оператора.
    """
    return (
        session.query(Contact)
        .filter(
            Contact.operator_id == operator_id,
            Contact.status == ContactStatus.open,
        )
        .count()
    )


def available_operators_for_source(session: Session, source_id: int) -> list:
    """
    Возвращает список доступных для источника операторов с их нагрузками.

    :param session: Сессия для работы с базой данных.
    :param source_id: ID источника.
    :return: Список операторов с их нагрузками.
    """
    rows = (
        session.query(SourceOperator)
        .filter(SourceOperator.source_id == source_id)
        .all()
    )
    opers = []
    for source_oper in rows:
        oper = source_oper.operator
        if not oper.active:
            continue
        current_load = count_active_contacts_for_operator(session, oper.id)
        if oper.limit is not None and current_load >= oper.limit:
            continue
        opers.append((oper, source_oper.weight))
    return opers


def choose_operator_by_weight(candidates: list) -> Operator | None:
    # Пока реализовал через random, что-то поинтереснее придумать не успел
    """
    Выбирает оператора из списка.

    :param candidates: Список операторов с их нагрузками.
    :return: Объект оператор или None.
    """
    if not candidates:
        return None
    total = sum(i_weight for _, i_weight in candidates)
    rand = random.uniform(0, total)
    upto = 0
    for i_oper, i_wight in candidates:
        if upto + i_wight >= rand:
            return i_oper
        upto += i_wight
    return candidates[-1][0]


def create_contact(session: Session, contact: ContactCreate) -> Contact:
    """
    Создаёт новый объект Contact и назначает оператора.

    :param session: Сессия для работы с базой данных.
    :param contact: Объект ContactCreate.
    :return: Объект Contact.
    """
    lead = find_or_create_lead(
        session, external_id=contact.external_id, e_mail=contact.e_mail
    )
    candidates = available_operators_for_source(session, contact.source_id)
    chosen = choose_operator_by_weight(candidates)
    operator_id = chosen.id if chosen else None
    contact = Contact(
        lead_id=lead.id,
        source_id=contact.source_id,
        operator_id=operator_id,
        payload=contact.payload,
    )
    session.add(contact)
    session.commit()
    session.refresh(contact)
    return contact


def get_leads_list(session: Session) -> list:
    """
    Получает список всех лидов.

    :param session: Сессия для работы с базой данных.
    :return: Список объектов Lead.
    """
    return session.query(Lead).all()


def get_stats(session: Session) -> dict:
    """
    Получает статистику по операторам и источникам.

    :param session: Сессия для работы с базой данных.
    :return: Словарь с операторами и источниками.
    """
    oper_list = session.query(Operator).all()
    sources = session.query(Source).all()
    oper_stats = []
    for i_oper in oper_list:
        total = (
            session.query(Contact)
            .filter(Contact.operator_id == i_oper.id)
            .count()
        )
        open_cnt = (
            session.query(Contact)
            .filter(
                Contact.operator_id == i_oper.id,
                Contact.status == ContactStatus.open,
            )
            .count()
        )
        oper_stats.append(
            {
                "operator_id": i_oper.id,
                "name": i_oper.name,
                "total": total,
                "open": open_cnt,
            }
        )
    source_stats = []
    for i_source in sources:
        total = (
            session.query(Contact)
            .filter(Contact.source_id == i_source.id)
            .count()
        )
        source_stats.append(
            {"source_id": i_source.id, "name": i_source.name, "total": total}
        )
    return {"operators": oper_stats, "sources": source_stats}
