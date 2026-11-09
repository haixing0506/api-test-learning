"""Use rows created in MySQL to drive login cases, then remove them again."""

import pytest

from config import BASE_URL
from db_helpers import login_log_count

LOGIN_URL = f"{BASE_URL}/api/user/login"
TEMP_USER = "auto_test_user"
PASSWORD = "123456"


def remove_temp_user(db, user_name):
    with db.cursor() as cursor:
        cursor.execute("delete from t_user_event_log where user_name = %s", (user_name,))
        cursor.execute("delete from t_user where user_name = %s", (user_name,))


@pytest.fixture()
def make_user(db):
    """Insert a user that reuses admin's encrypted password, clean up afterwards."""
    created = []

    def _make(status=1, deleted=0, user_name=TEMP_USER):
        remove_temp_user(db, user_name)
        with db.cursor() as cursor:
            cursor.execute(
                "insert into t_user"
                " (user_uuid, user_name, password, real_name, role, status, deleted, create_time)"
                " select uuid(), %s, password, %s, 1, %s, %s, now()"
                " from t_user where user_name = 'admin'",
                (user_name, "auto test", status, deleted),
            )
        created.append(user_name)
        return user_name

    yield _make

    for user_name in created:
        remove_temp_user(db, user_name)


def login(api, user_name, password=PASSWORD):
    payload = {"userName": user_name, "password": password, "remember": False}
    return api.post(LOGIN_URL, json=payload, timeout=10).json()


def test_active_temp_user_can_login(api, make_user):
    user_name = make_user()

    body = login(api, user_name)

    assert body["code"] == 1
    assert "JSESSIONID" in api.cookies


def test_disabled_user_cannot_login(api, db, make_user):
    user_name = make_user(status=2)
    before = login_log_count(db, user_name)

    body = login(api, user_name)

    assert body["code"] != 1
    assert "JSESSIONID" not in api.cookies
    assert login_log_count(db, user_name) == before


def test_soft_deleted_user_cannot_login(api, make_user):
    user_name = make_user(deleted=1)

    body = login(api, user_name)

    assert body["code"] != 1
    assert "JSESSIONID" not in api.cookies


@pytest.mark.xfail(
    strict=True,
    reason="defect: a status value outside 1/2 is treated as enabled, so login succeeds",
)
def test_unknown_status_value_is_rejected(api, make_user):
    user_name = make_user(status=0)

    body = login(api, user_name)

    assert body["code"] != 1
