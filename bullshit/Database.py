import sys
import cx_Oracle
from datetime import datetime
from numbers import Number
from typing import *
from Schema import Schema
from Model import MetaModel

# oracle_path = '/Users/glukianets/P/DB/distrib/instantclient_12_1'
# os.environ['DYLD_LIBRARY_PATH'] = oracle_path
# os.environ['NLS_LANG'] = oracle_path

import cx_Oracle


class Database:
    class Connection:
        class Cursor:
            def __init__(self, cursor, schema: Schema, variables: dict):
                self._cursor = cursor
                self._schema = schema
                self._variables = variables

            def __del__(self):
                self.dismiss()

            def __iter__(self):
                return self._cursor

            def __len__(self):
                return len(self._cursor)

            def fetch_all(self):
                return self._cursor.fetchall()

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
                return self._schema

            @property
            def variables(self):
                return self._variables

        def __init__(self, connection_string: str, schema_name: str = None):
            self._connection_string = connection_string
            self._schema_name = schema_name
            self._connection = None

        def __del__(self):
            self.close()

        def __enter__(self):
            return self if self.open() else None

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.close()

        def open(self):
            if self._connection is None:
                try:
                    self._connection = cx_Oracle.connect(self._connection_string)
                    # self._connection.autocommit = True
                    if self._schema_name is not None:
                        self._connection.current_schema = self._schema_name
                    return True
                except cx_Oracle.DatabaseError as err:
                    print(self._connection_string, ': ', err)
                    return False

        def close(self):
            if self._connection is not None:
                self._connection.close()
                self._connection = None

        def begin_transaction(self):
            if self._connection is not None:
                self._connection.begin()

        def commit_transaction(self):
            if self._connection is not None:
                self._connection.commit()

        def rollback_transaction(self):
            if self._connection is not None:
                self._connection.rollback()

        def perform_in_transaction(self, callable: Callable):
            self.begin_transaction()
            try:
                callable()
            except Exception as exception:
                print("Caught exception; rolling back transaction; \n" + str(exception))
                self.rollback_transaction()
                return False
            else:
                self.commit_transaction()
                return True

        def execute(self, string, vars=None, model=None, *args, **kwargs):
            cursor: cx_Oracle.Cursor = self._connection.cursor()

            variables = {name: cursor.var(type) for name, type in (vars or {}).items()}

            cursor.prepare(string)
            cursor.execute(None, *args, {**kwargs, **variables})

            schema = model.schema if model is not None else None
            schema = schema or Schema(cursor.description) if cursor.description is not None else None
            if schema is not None:
                model = model or MetaModel.create("AutoModel", schema)
                cursor.rowfactory = model

            return __class__.Cursor(cursor, schema, variables)

    @staticmethod
    def test():
        connection = cx_Oracle.connect(self._connectionString)
        print('ORACLE VERSION = ' + connection.version)
        connection.close()

    def __init__(self, **kwargs):
        self._connectionString = "{username}/{password}@{host}:{port}/{listener}".format(**kwargs)
        self._schema_name = kwargs['schema']

    def __str__(self):
        return "ORACLE DATABASE " + self._connection.clientversion()

    def connect(self):
        return __class__.Connection(self._connectionString, self._schema_name)