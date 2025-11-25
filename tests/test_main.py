"""Содержит тесты для проверки работы main.py."""

from fastapi.testclient import TestClient

from tests.conftest import (
    SUCCESS_CODE,
    OPERATOR_NAME,
    OPER_URL,
    OPER_ID,
    SOURCES_URL,
    ID,
    NAME,
    LIMIT,
    ACTIVE,
    EXTERNAL
)


def test_create_operator(client: TestClient):
    """Тест создания нового оператора."""
    response = client.post(
        OPER_URL,
        json={NAME: OPERATOR_NAME, ACTIVE: True, LIMIT: 5}
    )
    assert response.status_code == SUCCESS_CODE
    test_data = response.json()
    assert test_data[NAME] == OPERATOR_NAME
    assert test_data[ACTIVE] is True
    assert test_data[LIMIT] == 5


def test_list_operators(client: TestClient):
    """Тест получения списка операторов."""
    client.post(
        OPER_URL,
        json={NAME: OPERATOR_NAME, ACTIVE: True, LIMIT: 2}
    )
    response = client.get(OPER_URL)
    assert response.status_code == SUCCESS_CODE
    test_data = response.json()
    assert len(test_data) >= 1


def test_patch_operator(client: TestClient):
    """Тест обновления данных оператора."""
    response = client.post(
        OPER_URL,
        json={NAME: OPERATOR_NAME, ACTIVE: True, LIMIT: 2}
    )
    oper_id = response.json()[ID]
    patch_resp = client.patch(
        f"{OPER_URL}{oper_id}",
        json={NAME: OPERATOR_NAME, ACTIVE: False, LIMIT: 10}
    )
    assert patch_resp.status_code == SUCCESS_CODE
    test_data = patch_resp.json()
    assert test_data[ACTIVE] is False
    assert test_data[LIMIT] == 10


def test_create_source_and_assign_operator(client: TestClient):
    """Тест создания источника и назначения оператора."""
    oper_id = client.post(
        OPER_URL,
        json={NAME: OPERATOR_NAME, ACTIVE: True, LIMIT: 5}
    ).json()[ID]
    source_id = client.post(SOURCES_URL, json={NAME: "bot"}).json()[ID]
    assign_resp = client.post(
        f"{SOURCES_URL}{source_id}{OPER_URL}",
        json={OPER_ID: oper_id, "weight": 10}
    )
    assert assign_resp.status_code == SUCCESS_CODE
    test_data = assign_resp.json()
    assert test_data[OPER_ID] == oper_id


def test_register_contact_and_list_leads(client: TestClient):
    """Тест регистрации нового контакта."""
    oper_id = client.post(
        OPER_URL,
        json={NAME: OPERATOR_NAME, ACTIVE: True, LIMIT: 5}
    ).json()[ID]

    source_id = client.post(SOURCES_URL, json={NAME: "bot"}).json()[ID]

    client.post(
        f"{SOURCES_URL}{source_id}{OPER_URL}",
        json={OPER_ID: oper_id, "weight": 10}
    )

    lead_external_id = "lead1"

    contact_resp = client.post(
        "/contacts/",
        json={
            "external_id": lead_external_id,
            "source_id": source_id,
            "payload": "test_payload",
        },
    )
    assert contact_resp.status_code == SUCCESS_CODE

    test_data = contact_resp.json()
    assert test_data[OPER_ID] == oper_id

    leads_resp = client.get("/leads/")
    assert any(lead["external_id"] == lead_external_id for lead in leads_resp.json())


def test_stats(client: TestClient):
    """Тест корректности ответа эндпоинта `/stats/`."""
    response = client.get("/stats/")
    assert response.status_code == SUCCESS_CODE
    test_data = response.json()
    assert "operators" in test_data
    assert "sources" in test_data
