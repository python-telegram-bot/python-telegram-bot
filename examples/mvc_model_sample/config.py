import os


class BotConfig:
    token = os.environ.get("TOKEN", "YOUR TOKEN")


class DbConfig:
    db_user = os.environ.get('POSTGRES_USER', "")
    db_password = os.environ.get('POSTGRES_PASSWORD', "")
    db_host = os.environ.get('POSTGRES_HOST', "")
    db_name = os.environ.get('POSTGRES_DB', "")
    db_port = os.environ.get('POSTGRES_PORT', "")
    database_url = "postgresql://{}:{}@{}:{}/{}".format(db_user, db_password, db_host, db_port, db_name)
