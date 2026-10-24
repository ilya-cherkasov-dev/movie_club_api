import sqlite3

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

from settings import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


def unicode_lower(value):
    """Перевести строку в нижний регистр с учётом любых алфавитов."""
    return value.lower() if isinstance(value, str) else value


@event.listens_for(Engine, 'connect')
def set_sqlite_lower(dbapi_connection, connection_record):
    """Научить функцию lower() в SQLite работать с кириллицей."""
    # Встроенная lower() в SQLite понимает только латиницу, из-за этого
    # ilike не находил «Матрица» по запросу «матрица». Подменяю её
    # на питоновскую, которая знает все алфавиты.
    if isinstance(dbapi_connection, sqlite3.Connection):
        dbapi_connection.create_function(
            'lower', 1, unicode_lower, deterministic=True
        )


from . import api_views, cli_commands  # noqa: E402, F401
