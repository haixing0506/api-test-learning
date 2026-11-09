import requests

BASE_URL = "http://localhost:8000"


def test_admin_login_and_current_user():
    session = requests.Session()

    login_response = session.post(
        f"{BASE_URL}/api/user/login",
        json={
            "userName": "admin",
            "password": "123456",
            "remember": False,
        },
        timeout=10,
    )

    assert login_response.status_code == 200

    login_body = login_response.json()
    assert login_body["code"] == 1
    assert "JSESSIONID" in session.cookies

    current_response = session.post(
        f"{BASE_URL}/api/admin/user/current",
        timeout=10,
    )

    assert current_response.status_code == 200

    current_body = current_response.json()
    assert current_body["code"] == 1
    assert current_body["response"]["userName"] == "admin"
    assert current_body["response"]["role"] == 3