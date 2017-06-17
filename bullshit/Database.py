import sys
import cx_Oracle
from datetime import datetime
from numbers import Number
from typing import *

# oracle_path = '/Users/glukianets/P/DB/distrib/instantclient_12_1'
# os.environ['DYLD_LIBRARY_PATH'] = oracle_path
# os.environ['NLS_LANG'] = oracle_path

import cx_Oracle


def test_oracle():
    connection = cx_Oracle.connect('system/oracle@192.168.56.101:1521/orcl12c')
    print('ORACLE VERSION = ' + connection.version)
    connection.close()


class Schema:
    class Property:
        def __init__(self, name: str, typeobj: type, is_nullable: bool):
            self._name = name
            self._type = typeobj
            self._is_nullable = is_nullable

        def __str__(self):
            return self.name + ': ' + ('nullable ' if self.is_nullable else 'nonnull ') + str(self.type)

        @property
        def name(self):
            return self._name

        @property
        def type(self):
            return self._type

        @property
        def is_nullable(self):
            return self._is_nullable

    def __init__(self, oracle_schema: List[Tuple[str, type, bool]] = None):
        self._properties = [__class__.Property(x[0], __class__.native_type_for(x[1]), x[6] == 1) for x in oracle_schema]

    def __iter__(self):
        return iter(self._properties)

    def __str__(self):
        return super().__str__() + ' { ' + ', '.join([str(x) for x in self.properties]) + ' }'

    @property
    def properties_count(self):
        return len(self._properties)

    @property
    def properties(self):
        return self._properties

    @staticmethod
    def native_type_for(oracle_type: type) -> type:
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
        return type_objects_by_name.get(oracle_type)

    @staticmethod
    def car():
        return Schema([
            ('ID', cx_Oracle.NUMBER, 127, None, 0, -127, 0),
            ('NUM', cx_Oracle.NCHAR, 32, 32, None, None, 0),
            ('COLOR', cx_Oracle.NUMBER, 39, None, 38, 0, 0),
            ('MARK', cx_Oracle.NCHAR, 256, 256, None, None, 0),
            ('IS_FOREIGN', cx_Oracle.NUMBER, 2, None, 1, 0, 0),
        ])

    @staticmethod
    def service():
        return Schema([
            ('ID', cx_Oracle.NUMBER, 127, None, 0, -127, 0),
            ('NAME', cx_Oracle.NCHAR, 256, 256, None, None, 0),
            ('COST_OUR', cx_Oracle.NUMBER, 127, None, 0, -127, 0),
            ('COST_FOREIGN', cx_Oracle.NUMBER, 127, None, 0, -127, 0)
        ])

    @staticmethod
    def master():
        return Schema([
            ('ID', cx_Oracle.NUMBER, 127, None, 0, -127, 0),
            ('NAME', cx_Oracle.NCHAR, 256, 256, None, None, 0)
        ])

    @staticmethod
    def work():
        return Schema([
            ('ID', cx_Oracle.NUMBER, 127, None, 0, -127, 0),
            ('DATE_WORK', cx_Oracle.DATETIME, 23, None, None, None, 0),
            ('MASTER_ID',cx_Oracle.NUMBER, 127, None, 0, -127, 0),
            ('CAR_ID', cx_Oracle.NUMBER, 127, None, 0, -127, 0),
            ('SERVICE_ID', cx_Oracle.NUMBER, 127, None, 0, -127, 0)
        ])


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
        if self._cursor is not None:
            return Schema(self._cursor.description)


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