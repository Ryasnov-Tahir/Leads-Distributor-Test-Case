"""Конфигурация pytest для тестов приложения."""

import pytest
from typing import Generator
from functools import partial
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base
from app.main import app, get_session


# Константы для избежания повторений и магических чисел
OPERATOR_NAME = "Витя"
SOURCE_NAME = "bot"
EXTERNAL = "lead_id"
OPER_URL = "/operators/"
SOURCES_URL = "/sources/"
OPER_ID = "operator_id"
ID = "id"
NAME = "name"
ACTIVE = "active"
LIMIT = "limit"
SUCCESS_CODE = 200
WEIGHT = 20



SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


@pytest.fixture(scope="function")
def session():
    """
    Фикстура для создания тестовой сессии базы данных.

    Создаёт все таблицы перед тестом и удаляет их после теста.

    :yield: Тестовая сессия базы данных.
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def override_get_session(session: TestingSessionLocal) -> Generator:
    """
    Функция зависимости для получения сессии базы данных в тестах.

    :param session: Тестовая сессия базы данных.
    :yield: Тестовая сессия базы данных.
    """
    yield session


@pytest.fixture(scope="function")
def client(session):
    """
    Фикстура для тестового клиента с переопределённой зависимостью базы данных.

    :param session: Тестовая сессия базы данных.
    :return: Экземпляр тестовый клиент для выполнения запросов к приложению.
    """
    app.dependency_overrides[get_session] = partial(
        override_get_session,
        session
    )
    with TestClient(app) as test_client:
        yield test_client
