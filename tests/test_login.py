"""Login tests: check the HTTP response and the MySQL rows it should touch."""

from config import ADMIN, BASE_URL

LOGIN_URL = f"{BASE_URL}/api/user/login"
CURRENT_URL = f"{BASE_URL}/api/admin/user/current"


def login_log_count(db, user_name):
    with db.cursor() as cursor:
        cursor.execute(
            "select count(*) as total from t_user_event_log where user_name = %s",
            (user_name,),
        )
        return cursor.fetchone()["total"]


def latest_login_log(db, user_name):
    with db.cursor() as cursor:
        cursor.execute(
            "select user_name, real_name, content, create_time"
            " from t_user_event_log where user_name = %s order by id desc limit 1",
            (user_name,),
        )
        return cursor.fetchone()


def get_user(db, user_name):
    with db.cursor() as cursor:
        cursor.execute(
            "select id, user_name, real_name, role, status, deleted + 0 as deleted"
            " from t_user where user_name = %s and deleted = 0",
            (user_name,),
        )
        return cursor.fetchone()


def test_login_success_returns_code_1(api):
    response = api.post(LOGIN_URL, json=ADMIN, timeout=10)

    assert response.status_code == 200
    assert response.json()["code"] == 1
    assert "JSESSIONID" in api.cookies


def test_login_success_writes_one_login_log(api, db):
    before = login_log_count(db, "admin")

    body = api.post(LOGIN_URL, json=ADMIN, timeout=10).json()
    assert body["code"] == 1

    assert login_log_count(db, "admin") == before + 1

    log = latest_login_log(db, "admin")
    assert log["user_name"] == "admin"
    assert "admin" in log["content"]


def test_current_user_matches_database(admin_api, db):
    user = get_user(db, "admin")
    assert user is not None

    body = admin_api.post(CURRENT_URL, timeout=10).json()

    assert body["code"] == 1
    assert body["response"]["userName"] == user["user_name"]
    assert body["response"]["role"] == user["role"]
    assert body["response"]["realName"] == user["real_name"]


def test_login_wrong_password_is_rejected(api, db):
    before = login_log_count(db, "admin")
    payload = {"userName": "admin", "password": "wrong-password", "remember": False}

    response = api.post(LOGIN_URL, json=payload, timeout=10)
    body = response.json()

    assert response.status_code == 200
    assert body["code"] == 402
    assert "JSESSIONID" not in api.cookies
    assert login_log_count(db, "admin") == before


def test_login_unknown_user_is_rejected(api):
    payload = {"userName": "no_such_user", "password": "123456", "remember": False}
    body = api.post(LOGIN_URL, json=payload, timeout=10).json()

    assert body["code"] == 402
    assert "JSESSIONID" not in api.cookies


def test_current_user_requires_login(api):
    body = api.post(CURRENT_URL, timeout=10).json()

    assert body["code"] != 1
