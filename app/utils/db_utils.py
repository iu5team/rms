import abc
import sqlite3
from django.conf import settings


class Connection(object):
    obj = None
    DB_PATH = None

    def __init__(self):
        super(Connection, self).__init__()
        self.db_name = settings.DATABASES['default']['NAME'] if self.DB_PATH is None else self.DB_PATH
        self.conn = sqlite3.connect(self.db_name,
                                    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                                    check_same_thread=False)

    @classmethod
    def get_connection(cls):
        if cls.obj is None:
            cls.obj = Connection()
        return cls.obj.conn

    @staticmethod
    def get_cursor_description(cursor):
        if cursor.description is not None:
            return list(map(lambda l: list(l)[0], list(cursor.description)))
        return None

    @staticmethod
    def row_to_dict(row, desc):
        return dict(zip(desc, row))


class DoesNotExist(Exception):
    GATEWAY_CLASS = None

    def __init__(self, entity_id=None):
        self.entity_id = entity_id

    def __str__(self):
        if self.entity_id is not None:
            return "Entity of type '{}' with id {} not found".format(self.GATEWAY_CLASS.TABLE_NAME, self.entity_id)
        else:
            return "Entity of type '{}' does not exists".format(self.GATEWAY_CLASS.TABLE_NAME)

