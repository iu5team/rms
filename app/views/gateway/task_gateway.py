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
        result = cls.res_and_desc_to_result(res, desc)
        return result

    @classmethod
    def res_and_desc_to_result(cls, res, desc):
        result = []
        for row in res:
            d = Connection.row_to_dict(row, desc)
            d = cls(__exists__=True, **d)
            result.append(d)

        return result