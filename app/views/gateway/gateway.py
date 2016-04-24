import abc
import sqlite3
from django.conf import settings


class GatewayConnection(object):
    obj = None

    def __init__(self):
        super(GatewayConnection, self).__init__()
        self.db_name = settings.DATABASES['default']['NAME']
        self.conn = sqlite3.connect(self.db_name,
                                    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                                    check_same_thread=False)

    @classmethod
    def get_connection(cls):
        if cls.obj is None:
            cls.obj = GatewayConnection()
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


class Gateway(object):
    TABLE_NAME = None
    MAPPING = None

    DoesNotExist = None

    def __init__(self, **kwargs):
        super(Gateway, self).__init__()
        self.__exists__ = False
        self.__dirty__ = set()
        self._id = kwargs.get('id')

        cls = self.__class__

        class _DoesNotExist(DoesNotExist):
            GATEWAY_CLASS = cls

        self.DoesNotExist = _DoesNotExist

    @property
    def id(self):
        return self._id

    @property
    def conn(self):
        return self.get_conn()

    @classmethod
    def get_conn(cls):
        return GatewayConnection.get_connection()

    @classmethod
    def find_by_id(cls, id):
        c = cls.get_conn().cursor()
        res = c.execute("SELECT * FROM {} WHERE `id` = ?".format(cls.TABLE_NAME), [id])
        desc = GatewayConnection.get_cursor_description(res)
        row = res.fetchone()
        if row is None:
            raise cls().DoesNotExist(id)
        d = GatewayConnection.row_to_dict(row, desc)
        return cls(__exists__=True, **d)

    def save(self):
        if self.__exists__:
            if self.id is None:
                raise self.DoesNotExist()

            if len(self.__dirty__) > 0:
                update_sql = []
                update_args = []
                for attr in self.__dirty__:
                    update_sql.append('{} = ?'.format(attr))
                    update_args.append(getattr(self, '_' + attr))
                update_sql = ','.join(update_sql)
                update_args.append(self.id)

                self.conn.execute("""
                  UPDATE {} SET {} WHERE `id` = ?
                """.format(self.TABLE_NAME, update_sql),
                                  update_args)
                self.conn.commit()
        else:
            insert_sql = []
            insert_sql_values = []
            insert_args = []
            for _, attr_name in iter(self.MAPPING.items()):
                if attr_name != 'id':
                    insert_sql.append(attr_name)
                    insert_sql_values.append('?')
                    insert_args.append(getattr(self, '_' + attr_name))
            insert_sql = ','.join(insert_sql)
            insert_sql_values = ','.join(insert_sql_values)

            c = self.conn.cursor()
            c.execute("""
                INSERT INTO {} ({}) VALUES ({})
              """.format(self.TABLE_NAME, insert_sql, insert_sql_values),
                      insert_args)
            self.conn.commit()
            self._id = c.lastrowid
            self.__exists__ = True
            pass

    @abc.abstractmethod
    def delete(self, *args, **kwargs):
        if not self.__exists__ or self.id is None:
            raise self.DoesNotExist()

        self.conn.execute("DELETE FROM {} WHERE `id` = ?".format(self.TABLE_NAME), [self.id])
        self.conn.commit()
        self.__exists__ = False
