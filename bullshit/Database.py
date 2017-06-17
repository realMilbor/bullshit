import sys
import cx_Oracle
from datetime import datetime
from numbers import Number

# oracle_path = '/Users/glukianets/P/DB/distrib/instantclient_12_1'
# os.environ['DYLD_LIBRARY_PATH'] = oracle_path
# os.environ['NLS_LANG'] = oracle_path

import cx_Oracle


def test_oracle():
    connection = cx_Oracle.connect('system/oracle@192.168.56.101:1521/orcl12c')
    print('ORACLE VERSION = ' + connection.version)
    connection.close()


class DatabaseCursor:
    def __init__(self, cursor):
        self._cursor = cursor

    def __del__(self):
        self.dismiss()

    def __iter__(self):
        return self._cursor

    def __len__(self):
        return len(self._cursor)

    def dismiss(self):
        if self._cursor is not None:
            try:
                self._cursor.close()
            except cx_Oracle.DatabaseError:
                pass
            finally:
                self._cursor = None

    @property
    def schema(self):
        def resolve_type_object(type_name: str) -> type:
            type_objects_by_name = {
                cx_Oracle.NUMBER: Number,
                cx_Oracle.STRING: str,
                cx_Oracle.FIXED_CHAR: str,
                cx_Oracle.NCHAR: str,
                cx_Oracle.DATETIME: datetime,
                cx_Oracle.TIMESTAMP: datetime,
                cx_Oracle.CLOB: None,
                cx_Oracle.BLOB: None,
            }
            return type_objects_by_name.get(type_name)

        if self._cursor is not None:
            return [(x[0], resolve_type_object(x[1]), x[6] == 1) for x in self._cursor.description]


class Database:
    def __init__(self, **kwargs):
        self._connection = None
        self._connectionString = "{username}/{password}@{host}:{port}/{listener}".format(**kwargs)

    def __enter__(self):
        try:
            self._connection = cx_Oracle.connect(self._connectionString)
            return self
        except cx_Oracle.DatabaseError as err:
            print(self._connectionString, ': ', err)
            return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._connection is not None:
            self._connection.close()

    def __str__(self):
        return "ORACLE DATABASE " + self._connection.clientversion()

    def execute(self, string, *args, **kwargs):
        cursor = self._connection.cursor()
        cursor.prepare(string)
        cursor.execute(None, *args, **kwargs)
        return DatabaseCursor(cursor)


class DBAccessor:
    def __init__(self, db):
        self.db = db

    def schema_works():
        return ('ID', 'DATE', 'MASTER ID', 'CAR_ID', 'SERVICE_ID')

    def all_works(self):
        return


