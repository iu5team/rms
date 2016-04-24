import datetime

from app.views.gateway.gateway import Gateway, GatewayConnection


class TaskGateway(Gateway):
    TABLE_NAME = 'app_task'
    MAPPING = {
        0: 'id',
        1: 'creation_date',
        2: 'status',
        3: 'description',
        4: 'title',
        5: 'assignee_id',
        6: 'finish_date',
    }

    def __init__(self, **kwargs):
        super(TaskGateway, self).__init__(**kwargs)
        self._creation_date = kwargs.get('creation_date')
        self._finish_date = kwargs.get('finish_date')
        self._status = kwargs.get('status')
        self._description = kwargs.get('description')
        self._title = kwargs.get('title')
        self._assignee_id = kwargs.get('assignee_id')
        self.__exists__ = kwargs.get('__exists__', False)

    @property
    def creation_date(self):
        return self._creation_date

    @creation_date.setter
    def creation_date(self, creation_date):
        self._creation_date = creation_date
        self.__dirty__.add('creation_date')

    @property
    def finish_date(self):
        return self._finish_date

    @finish_date.setter
    def finish_date(self, finish_date):
        self._finish_date = finish_date
        self.__dirty__.add('finish_date')

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status
        self.__dirty__.add('status')

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        self._description = description
        self.__dirty__.add('description')

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title
        self.__dirty__.add('title')

    @property
    def assignee_id(self):
        return self._assignee_id

    @assignee_id.setter
    def assignee_id(self, assignee_id):
        self._assignee_id = assignee_id
        self.__dirty__.add('assignee_id')

    @classmethod
    def find_by_title(cls, title, contains=False):
        c = cls.get_conn().cursor()
        query_args = []
        if contains:
            query_sql = " LIKE '%{}%'".format(title)  # Security breach - should be escaping
        else:
            query_sql = " = ?"
            query_args.append(title)
        res = c.execute("SELECT * FROM {} WHERE `title` {}".format(cls.TABLE_NAME, query_sql), query_args)
        desc = GatewayConnection.get_cursor_description(res)
        result = []
        for row in res:
            d = GatewayConnection.row_to_dict(row, desc)
            d = cls(__exists__=True, **d)
            result.append(d)
        return result

