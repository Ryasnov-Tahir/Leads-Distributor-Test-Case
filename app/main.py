"""Содержит точку входа для работы программы."""

from fastapi import FastAPI, Depends, HTTPException
from app.database import SessionLocal, engine, Base
from sqlalchemy.orm import Session
from app.schemas import (
    OperatorOut,
    SourceOut,
    SourceOperatorAssign,
    ContactOut,
    LeadOut,
    OperatorCreate,
    SourceCreate,
    ContactCreate,
)
from app.crud import (
    create_operator,
    get_opers_list,
    update_operator,
    create_source,
    assign_operator_to_source,
    create_contact,
    get_leads_list,
    get_stats,
)
from app.models import Source

NOT_FOUND = 404


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Leads Distributor")


def get_session() -> Session:
    """
    Получает сессию для работы с базой данных.

    :yield: Объект сессии для работы с базой данных.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


db_session = Depends(get_session)


@app.post("/operators/", response_model=OperatorOut)
def create_operator_endpoint(
    oper: OperatorCreate, session: Session = db_session
) -> OperatorOut:
    """
    Создаёт нового оператора.

    :param oper: Данные для создания оператора.
    :param session: Сессия для работы с базой данных.
    :return: Объект оператора.
    """
    return create_operator(session=session, oper=oper)


@app.get("/operators/", response_model=list[OperatorOut])
def list_ops(session: Session = db_session) -> list:
    """
    Получает список всех операторов.

    :param session: Сессия для работы с базой данных.
    :return: Список операторов.
    """
    return get_opers_list(session=session)


@app.patch("/operators/{operator_id}", response_model=OperatorOut)
def patch_operator(
    operator_id: int,
        oper: OperatorCreate,
        session: Session = db_session
) -> OperatorOut:
    """
    Обновляет параметры оператора.

    :param operator_id: ID оператора.
    :param oper: Модель данных оператора.
    :param session: Сессия для работы с базой данных.
    :return: Объект оператора.
    :raises HTTPException: Если оператор с указанным ID не найден.
    """
    update = update_operator(
        session=session,
        operator_id=operator_id,
        active=oper.active,
        limit=oper.limit
    )
    if not update:
        raise HTTPException(status_code=NOT_FOUND, detail="Operator not found")
    return update


@app.post("/sources/", response_model=SourceOut)
def create_source_endpoint(
    source: SourceCreate, session: Session = db_session
) -> SourceOut:
    """
    Создаёт новый источник.

    :param source: Данные для создания источника.
    :param session: Сессия для работы с базой данных.
    :return: Объект источника.
    :raises sqlalchemy.exc.SQLAlchemyError: При ошибках взаимодействия с базой.
    """
    return create_source(session=session, source_create=source)


@app.post("/sources/{source_id}/operators/")
def assign_operator(
    source_id: int,
        assign: SourceOperatorAssign,
        session: Session = db_session
) -> dict:
    """
    Назначает оператору нагрузку для источника.

    :param source_id: ID источника.
    :param assign: Данные о назначаемом операторе и его нагрузке.
    :param session: Сессия для работы с базой данных.
    :return: Словарь с данными о созданной связи источник–оператор.
    :raises HTTPException: Если оператор или источник не найдены.
    """
    source_oper = assign_operator_to_source(
        session=session,
        source_id=source_id,
        assign=assign
    )
    if not source_oper:
        raise HTTPException(
            status_code=NOT_FOUND,
            detail="Operator or Source not found"
        )
    return {
        "id": source_oper.id,
        "source_id": source_oper.source_id,
        "operator_id": source_oper.operator_id,
        "weight": source_oper.weight,
    }


@app.post("/contacts/", response_model=ContactOut)
def register_contact(
    contact: ContactCreate, session: Session = db_session
) -> ContactOut:
    """
    Регистрирует новый контакт от лида.

    :param contact: Данные для создания контакта.
    :param session: Сессия для работы с базой данных.
    :return: Созданный контакт.
    :raises HTTPException: Если указанный источник не существует.
    """
    source = (session.query(Source).
              filter(Source.id == contact.source_id).
              first())
    if not source:
        raise HTTPException(status_code=NOT_FOUND, detail="Source not found")
    res_contact = create_contact(session=session, contact=contact)
    return res_contact


@app.get("/leads/", response_model=list[LeadOut])
def list_leads(session: Session = db_session) -> list:
    """
    Возвращает список всех лидов.

    :param session: Сессия для работы с базой данных.
    :return: Список лидов.
    """
    return get_leads_list(session=session)


@app.get("/stats/")
def get_stats_endpoint(session: Session = db_session) -> dict:
    """
    Возвращает статистику по лидам, обращениям и операторам.

    :param session: Сессия для работы с базой данных.
    :return: Словарь со статистическими данными.
    """
    return get_stats(session=session)
