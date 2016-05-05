# coding=utf-8
##
# @file
# @brief Gateway для работы с базой данных

from app.utils.db_utils import *


##
# @brief Базовый класс для работы с БД
#
# Отображает строку таблицы БД в объект

class Gateway(object):
    TABLE_NAME = None
    FIELDS = None

    DoesNotExist = None

    def __init__(self, **kwargs):
        super(Gateway, self).__init__()
        self.__exists__ = False
        self.__dirty__ = set()

        self._id = kwargs.get('id')
        self._fields = {}
        for field_name in self.FIELDS:
            field_value = kwargs.get(field_name)
            self._fields[field_name] = field_value

        self.__exists__ = kwargs.pop('__exists__', False)
        cls = self.__class__

        class _DoesNotExist(DoesNotExist):
            GATEWAY_CLASS = cls

        self.DoesNotExist = _DoesNotExist

    def __getattribute__(self, key):
        try:
            return super(Gateway, self).__getattribute__(key)
        except AttributeError:
            if key in self.FIELDS:
                return self._fields[key]
            else:
                raise AttributeError('Attribute {} is unknown'.format(key))

    def __setattr__(self, key, value):
        if key in self.FIELDS:
            self._fields[key] = value
            self.__dirty__.add(key)
        else:
            return super(Gateway, self).__setattr__(key, value)

    @property
    def conn(self):
        return self.get_conn()

    @classmethod
    def get_conn(cls):
        return Connection.get_connection()

    ##
    # @brief find_by_id - Поиск по id
    #
    # Ищет запись текущего класса по id
    # @param id - id сущности
    # @return Объект типа Gateway
    #
    #
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

    ##
    # @brief save - Сохранить объект в БД
    #
    # Если запись уже существовала, что она будет обновлена,
    # иначе - вставится новая запись
    # @return Объект типа Gateway
    #
    #
    def save(self):
        if self.__exists__:
            if self.id is None:
                raise self.DoesNotExist()

            if len(self.__dirty__) > 0:
                update_sql = []
                update_args = []
                for attr in self.__dirty__:
                    update_sql.append('{} = ?'.format(attr))
                    update_args.append(self._fields[attr])
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
            for attr_name in self.FIELDS:
                if attr_name != 'id':
                    insert_sql.append(attr_name)
                    insert_sql_values.append('?')
                    insert_args.append(self._fields[attr_name])
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

    ##
    # @brief delete - Удаляет объект из БД
    #
    #
    def delete(self, *args, **kwargs):
        if not self.__exists__ or self.id is None:
            raise self.DoesNotExist()

        self.conn.execute("DELETE FROM {} WHERE `id` = ?".format(self.TABLE_NAME), [self.id])
        self.conn.commit()
        self.__exists__ = False

    ##
    # @brief find_by_fields - Поиск по полям сущности
    #
    # Можно передать словарь атрибутов, который будут объедены через AND
    #
    # @code
    # {.py}
    # obj.find_by_fields(attr1='value1', attr2='value2')
    # @endcode
    #
    @classmethod
    def find_by_fields(cls, **fields):
        if len(fields) == 0:
            return None

        c = cls.get_conn().cursor()
        query_args = []
        query_sql = []

        for field_name, field_value in fields.items():
            query_sql.append('`{}` = ?'.format(field_name))
            query_args.append(field_value)

        query_sql = ' AND '.join(query_sql)

        res = c.execute("SELECT * FROM {} WHERE ({})".format(cls.TABLE_NAME, query_sql), query_args)
        desc = Connection.get_cursor_description(res)
        result = []
        for row in res:
            d = Connection.row_to_dict(row, desc)
            d = cls(__exists__=True, **d)
            result.append(d)
        return result
