import sqlite3
import os
from functools import cache

SCHEME_QUERIES = [
    """CREATE TABLE "SECRETS" ("id"	INTEGER NOT NULL UNIQUE,"key" TEXT NOT NULL UNIQUE,"value" TEXT NOT NULL,
    "chat_id" TEXT NOT NULL,PRIMARY KEY("id" AUTOINCREMENT))
""",
]


def init_database(path: str, force: bool = False):
    if not os.path.exists(path):
        __execute_create_tables(path)
    if force:
        __execute_create_tables(path)


def __execute_create_tables(path):
    db = sqlite3.connect(path)

    cur = db.cursor()

    for query in SCHEME_QUERIES:
        cur.execute(query)
    db.commit()
    cur.close()
    db.close()


@cache
def get_connection(path: str) -> sqlite3.Connection:
    return sqlite3.connect(path)


def get_cursor(path: str) -> sqlite3.Cursor:
    return get_connection(path).cursor()
