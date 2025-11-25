"""Содержит тесты для проверки работы crud.py."""

from sqlalchemy.orm import Session
from app import crud, schemas
from tests.conftest import OPERATOR_NAME, SOURCE_NAME, WEIGHT, EXTERNAL


class DummyOper:
    """Отдельный класс только для test_choose_operator_by_weight."""

    def __init__(self, oper_id):
        """
        Инициализация DummyOper.

        :param oper_id: ID оператора.
        """
        self.id = oper_id


def test_create_and_get_operator(session: Session):
    """Тест создания оператора."""
    oper_info = schemas.OperatorCreate(name="Alice", active=True, limit=5)
    oper = crud.create_operator(session, oper_info)
    assert oper.id is not None
    assert oper.name == "Alice"

    fetched = crud.get_operator(session, oper.id)
    assert fetched.id == oper.id
    assert fetched.name == "Alice"


def test_list_operators(session: Session):
    """Тест получения списка операторов из базы данных."""
    crud.create_operator(session, schemas.OperatorCreate(name=OPERATOR_NAME))
    crud.create_operator(session, schemas.OperatorCreate(name="Вася"))
    opers = crud.get_opers_list(session)
    assert len(opers) == 2
    names = [i_oper.name for i_oper in opers]
    assert "Витя" in names and "Вася" in names


def test_update_operator(session: Session):
    """Тест обновления полей оператора."""
    oper = crud.create_operator(
        session,
        schemas.OperatorCreate(name=OPERATOR_NAME, active=True, limit=2)
    )
    updated = crud.update_operator(session, oper.id, active=False, limit=10)
    assert updated.active is False
    assert updated.limit == 10


def test_create_source_and_assign_operator(session: Session):
    """Тест создания источника и назначение оператора."""
    oper = crud.create_operator(
        session,
        schemas.OperatorCreate(name=OPERATOR_NAME)
    )
    source = crud.create_source(
        session,
        schemas.SourceCreate(name=SOURCE_NAME)
    )
    source_oper = crud.assign_operator_to_source(
        session,
        source.id,
        schemas.SourceOperatorAssign(operator_id=oper.id, weight=WEIGHT)
    )
    assert source_oper.id is not None
    assert source_oper.source_id == source.id
    assert source_oper.operator_id == oper.id
    assert source_oper.weight == WEIGHT


def test_find_or_create_lead(session):
    """Тест повторного вызова с одинаковым external_id."""
    lead1 = crud.find_or_create_lead(session, external_id="same_id")
    lead2 = crud.find_or_create_lead(session, external_id="same_id")
    assert lead1.id == lead2.id


def test_count_active_contacts_for_operator(session):
    """Тест подсчёта активных контактов у оператора."""
    oper = crud.create_operator(
        session,
        schemas.OperatorCreate(name="Витя", limit=2)
    )
    crud.find_or_create_lead(session, external_id=EXTERNAL)
    source = crud.create_source(
        session,
        schemas.SourceCreate(name=SOURCE_NAME)
    )
    crud.assign_operator_to_source(
        session,
        source.id,
        schemas.SourceOperatorAssign(operator_id=oper.id, weight=10)
    )
    crud.create_contact(
        session,
        schemas.ContactCreate(external_id=EXTERNAL, source_id=source.id)
    )
    count = crud.count_active_contacts_for_operator(session, oper.id)
    assert count == 1


def test_available_operators_for_source(session):
    """
    Тест, что оператор доступен для источника.

    Но только до достижения лимита активных контактов.
    """
    oper = crud.create_operator(
        session,
        schemas.OperatorCreate(name=OPERATOR_NAME, limit=1)
    )
    source = crud.create_source(
        session,
        schemas.SourceCreate(name=SOURCE_NAME)
    )
    crud.assign_operator_to_source(
        session,
        source.id,
        schemas.SourceOperatorAssign(operator_id=oper.id, weight=10)
    )
    available = crud.available_operators_for_source(session, source.id)
    assert len(available) == 1
    crud.create_contact(
        session,
        schemas.ContactCreate(external_id=EXTERNAL, source_id=source.id)
    )
    available2 = crud.available_operators_for_source(session, source.id)
    assert len(available2) == 0


def test_choose_operator_by_weight():
    """Тест, что из списка кандидатов выбирается оператор с учётом нагрузки."""
    oper1 = DummyOper(1)
    oper2 = DummyOper(2)

    candidates = [(oper1, 10), (oper2, 30)]
    chosen = crud.choose_operator_by_weight(candidates)
    assert chosen.id in (1, 2)


def test_create_contact_and_stats(session):
    """Тест создания контакта и распределения лидов."""
    oper = crud.create_operator(
        session,
        schemas.OperatorCreate(name=OPERATOR_NAME, limit=5)
    )
    source = crud.create_source(
        session,
        schemas.SourceCreate(name=SOURCE_NAME)
    )
    crud.assign_operator_to_source(
        session,
        source.id,
        schemas.SourceOperatorAssign(operator_id=oper.id, weight=10)
    )
    contact = crud.create_contact(
        session,
        schemas.ContactCreate(
            external_id=EXTERNAL, source_id=source.id, payload="test_payload"
        ),
    )
    assert contact.id is not None
    stats = crud.get_stats(session)
    assert stats["operators"][0]["total"] == 1
    assert stats["sources"][0]["total"] == 1
