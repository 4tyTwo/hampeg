import sqlite3
import os
from hampegUtils import formatWildcards, formatFields
from sqlite3 import Error

def connectToDb(database):
    if not(os.path.isfile(database)):
        print("No database", database, "exists")
        exit(1)
    try:
        conn = sqlite3.connect(database)
    except Error as e:
        print(e)
        exit(1)
    return conn

def tableExists(dbcon, table_name):
    dbcur = dbcon.cursor()
    t = (table_name, )
    dbcur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", t)
    fetch = (dbcur.fetchone())
    if (fetch != None):
        if (fetch[0] == table_name):
            dbcur.close()
            return True
    dbcur.close()
    return False

def setupDb(database, table_name):
    conn = connectToDb(database)
    if not(tableExists(conn, table_name)):
        print("No table", table_name, "exists")
        exit(1)
    return conn

def insert(dbcon, table_name, record):
    fields = formatFields(record)
    values = list(record.values())
    wildcards = formatWildcards(values)
    qs = "INSERT INTO " + table_name + "(" + fields + ")" + " VALUES (" + wildcards + ")"
    c = dbcon.cursor()
    c.executemany(qs, (values,))
    dbcon.commit()
    c.close()

def recordId(dbcon, table_name, record):
    keys = list(record.keys())
    qs = "Select ID from " + table_name + " where "
    kvs = []
    for key in keys:
        kvs.append("=".join([key, "'" + str(record[key])]) + "'")
    qs += " and ".join(kvs)
    c = dbcon.cursor()
    c.execute(qs)
    fetch = (c.fetchone())
    if fetch != None:
        i = int(fetch[0])
        c.close()
        return i
    else:
        c.close()
        return -1
