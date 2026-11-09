"""Test configuration for the xzs API and its MySQL database."""

BASE_URL = "http://localhost:8000"

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "root",
    "database": "xzs",
    "charset": "utf8mb4",
}

ADMIN = {
    "userName": "admin",
    "password": "123456",
    "remember": False,
}
