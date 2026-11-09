"""Negative login cases, one data row per test run."""

import pytest

from config import BASE_URL
from db_helpers import user_row_count

LOGIN_URL = f"{BASE_URL}/api/user/login"

INVALID_CASES = [
    pytest.param("admin", "wrong-password", id="wrong-password"),
    pytest.param("no_such_user", "123456", id="unknown-user"),
    pytest.param("", "123456", id="empty-user-name"),
    pytest.param("admin", "", id="empty-password"),
    pytest.param("admin", None, id="missing-password"),
    pytest.param("' or '1'='1", "123456", id="sql-injection"),
    pytest.param("a" * 1000, "123456", id="long-user-name"),
]


@pytest.mark.parametrize("user_name,password", INVALID_CASES)
def test_invalid_login_is_rejected(api, user_name, password):
    payload = {"userName": user_name, "password": password, "remember": False}

    response = api.post(LOGIN_URL, json=payload, timeout=10)
    body = response.json()

    assert response.status_code == 200
    assert body["code"] == 402
    assert "JSESSIONID" not in api.cookies


def test_sql_injection_does_not_change_user_table(api, db):
    before = user_row_count(db)
    payload = {"userName": "' or '1'='1", "password": "123456", "remember": False}

    api.post(LOGIN_URL, json=payload, timeout=10)

    assert user_row_count(db) == before
