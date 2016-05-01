import datetime

from app.views.gateway.gateway import Gateway, Connection


class TaskGateway(Gateway):
    TABLE_NAME = 'app_task'
    FIELDS = {
        'id',
        'creation_date',
        'status',
        'description',
        'title',
        'assignee_id',
        'finish_date',
        'wasted_days',
    }

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
        desc = Connection.get_cursor_description(res)
        result = []
        for row in res:
            d = Connection.row_to_dict(row, desc)
            d = cls(__exists__=True, **d)
            result.append(d)
        return result


class SpentTimeArguments:

    class BadArguments(Exception):
        pass

    def __init__(self, task_id, assignee_id, days):
        self.task_id = self._parse_task_id(task_id)
        self.assignee_id = self._parse_assignee_id(assignee_id)
        self.days = self._parse_days(days)

    def _parse_task_id(self, task_id):
        try:
            return int(task_id)
        except ValueError:
            raise self.BadArguments("Bad task_id")

    def _parse_assignee_id(self, assignee_id):
        if assignee_id is None:
            raise self.BadArguments("Bad assignee_id")
        try:
            return int(assignee_id)
        except ValueError:
            raise self.BadArguments("Bad assignee_id")

    def _parse_days(self, days):
        if days is None:
            raise self.BadArguments("Bad assignee_id")
        try:
            return int(days)
        except ValueError:
            raise self.BadArguments("Bad days")
