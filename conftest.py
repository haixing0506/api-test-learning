import pymysql
import pytest
import requests
from pymysql.cursors import DictCursor

from config import ADMIN, BASE_URL, DB_CONFIG


@pytest.fixture()
def api():
    """One HTTP session per test, so cookies never leak between tests."""
    with requests.Session() as session:
        yield session


@pytest.fixture()
def db():
    """MySQL connection with dict rows, closed after the test."""
    connection = pymysql.connect(cursorclass=DictCursor, autocommit=True, **DB_CONFIG)
    try:
        yield connection
    finally:
        connection.close()


@pytest.fixture()
def admin_api(api):
    """Session that is already logged in as admin."""
    body = api.post(f"{BASE_URL}/api/user/login", json=ADMIN, timeout=10).json()
    assert body["code"] == 1, f"admin login failed: {body}"
    return api
