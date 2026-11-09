"""SQL helpers shared by the test modules."""


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
    """Return the row the login query would see: only rows with deleted = 0."""
    with db.cursor() as cursor:
        cursor.execute(
            "select id, user_name, real_name, role, status, deleted + 0 as deleted"
            " from t_user where user_name = %s and deleted = 0",
            (user_name,),
        )
        return cursor.fetchone()


def user_row_count(db):
    with db.cursor() as cursor:
        cursor.execute("select count(*) as total from t_user")
        return cursor.fetchone()["total"]
