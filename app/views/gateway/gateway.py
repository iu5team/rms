from app.utils.db_utils import *


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
        return Connection.get_connection()

    @classmethod
    def find_by_id(cls, id):
        c = cls.get_conn().cursor()
        res = c.execute("SELECT * FROM {} WHERE `id` = ?".format(cls.TABLE_NAME), [id])
        desc = Connection.get_cursor_description(res)
        row = res.fetchone()
        if row is None:
            raise cls().DoesNotExist(id)
        d = Connection.row_to_dict(row, desc)
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
