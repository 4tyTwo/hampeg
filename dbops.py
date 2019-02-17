import sqlite3
import os
from sqlite3 import Error

def connect_db(database):
    if not(os.path.isfile(database)):
        print("No database", database, "exists")
        exit(1)
    try:
        conn = sqlite3.connect(database)
    except Error as e:
        print(e)
        exit(1)
    return conn

def check_table_exists(dbcon, table_name):
    dbcur = dbcon.cursor()
    t = (table_name, )
    dbcur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", t)
    fetch = (dbcur.fetchone())
    if (fetch != None):
        if (fetch[0] == table_name):
            dbcur.close()
            return
    dbcur.close()
    print("No table", table_name, "exists")
    exit(1)

def setup_database(database, table_name):
    conn = connect_db(database)
    check_table_exists(conn, table_name)
    return conn
