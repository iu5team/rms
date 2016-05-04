from app.utils.db_utils import Connection


class Model(object):
    __table__ = None

    def __init__(self, **kwargs):
        super(Model, self).__init__()

        self.__exists__ = False
        self.__dirty__ = set()

        self._id = kwargs.get('id')

        self.__exists__ = kwargs.pop('__exists__', False)
        cls = self.__class__

        for field in kwargs:
            setattr(self, field, kwargs[field])

    def __getattribute__(self, key):
        return super(Model, self).__getattribute__(key)

    def __setattr__(self, key, value):
        res = super(Model, self).__setattr__(key, value)

        # if construction is done
        if '__dirty__' in vars(self):
            self.__dirty__.add(key)

    @classmethod
    def get(cls, id):
        c = Connection.get_connection().cursor()
        res = c.execute("SELECT * FROM {} WHERE `id` = ? LIMIT 1".format(cls.__table__), [id])
        desc = Connection.get_cursor_description(res)
        row = res.fetchone()
        if row is None:
            raise 'Unable to find: {}'.format(id)

        d = Connection.row_to_dict(row, desc)
        return cls(__exists__=True, **d)

    def create(self):
        insert_sql = []
        insert_sql_values = []
        insert_args = []
        for attr_name in vars(self).keys():
            if attr_name != 'id' and not attr_name.startswith('__'):
                insert_sql.append(attr_name)
                insert_sql_values.append('?')
                insert_args.append(self.__dict__[attr_name])
        insert_sql = ','.join(insert_sql)
        insert_sql_values = ','.join(insert_sql_values)

        c = self.conn.cursor()
        c.execute("""
                    INSERT INTO {} ({}) VALUES ({})
                  """.format(self.__table__, insert_sql, insert_sql_values),
                  insert_args)
        self.conn.commit()
        self._id = c.lastrowid
        self.__exists__ = True

    def update(self):
        if self.__exists__:
            if self.id is None:
                raise Exception('Unable to save')

            if len(self.__dirty__) > 0:
                update_sql = []
                update_args = []
                for attr in self.__dirty__:
                    if not attr_name.startswith('__'):
                        update_sql.append('{} = ?'.format(attr))
                        update_args.append(self.__dict__[attr])
                update_sql = ','.join(update_sql)
                update_args.append(self.id)

                self.conn.execute("""
                  UPDATE {} SET {} WHERE `id` = ?
                """.format(self.__table__, update_sql),
                                  update_args)
                self.conn.commit()
        else:
            self.create()

    def delete(self, *args, **kwargs):
        if not self.__exists__ or self.id is None:
            raise Exception('Unable to delete')

        self.conn.execute("DELETE FROM {} WHERE `id` = ?".format(self.__table__), [self.id])
        self.conn.commit()
        self.__exists__ = False

    @classmethod
    def find_by_fields(cls, **fields):
        if len(fields) == 0:
            return None

        c = Connection.get_connection().cursor()
        query_args = []
        query_sql = []

        for field_name, field_value in fields.items():
            query_sql.append('`{}` = ?'.format(field_name))
            query_args.append(field_value)

        query_sql = ' AND '.join(query_sql)

        res = c.execute("SELECT * FROM {} WHERE ({})".format(cls.__table__, query_sql), query_args)
        desc = Connection.get_cursor_description(res)
        result = []
        for row in res:
            d = Connection.row_to_dict(row, desc)
            d = cls(__exists__=True, **d)
            result.append(d)
        return result


