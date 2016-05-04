from app.utils.db_utils import Connection
from app.views.alekseyl.active_record.model import Model


class Task(Model):
    __table__ = 'app_task'

    def __init__(self, **kwargs):
        self.id = None
        self.creation_date = None
        self.finish_date = None
        self.status = None
        self.description = None
        self.title = None
        self.assignee_id = None
        self.wasted_days = None

        super(Task, self).__init__(**kwargs)

    @staticmethod
    def find(from_date, to_date, assignee_id=None):
        conn = Connection.get_connection()
        cursor = conn.cursor()

        if assignee_id is not None:
            res = cursor.execute(
                'SELECT * FROM app_task as t ' +
                'JOIN app_employee as e on e.id = t.assignee_id ' +
                'WHERE assignee_id = ? and creation_date >= ? and finish_date <= ?',
                (assignee_id, from_date, to_date))
        else:
            res = cursor.execute(
                'SELECT * FROM app_task as t ' +
                'JOIN app_employee as e on e.id = t.assignee_id ' +
                'WHERE assignee_id IS NOT NULL and creation_date >= ? and finish_date <= ?',
                (from_date, to_date))

        desc = Connection.get_cursor_description(res)

        tasks = []
        for row in res:
            data = Connection.row_to_dict(row, desc)
            task = Task(**data)
            tasks.append(task)

        return tasks

    @staticmethod
    def find_by_assignee(assignee_id):
        conn = Connection.get_connection()
        cursor = conn.cursor()

        res = cursor.execute(
            'SELECT * FROM app_task as t ' +
            'WHERE assignee_id = ?',
            (assignee_id,))

        desc = Connection.get_cursor_description(res)

        tasks = []
        for row in res:
            data = Connection.row_to_dict(row, desc)
            task = Task(**data)
            tasks.append(task)

        return tasks

    @staticmethod
    def find_by_title(title):
        conn = Connection.get_connection()
        cursor = conn.cursor()

        res = cursor.execute('SELECT * FROM app_task WHERE `title` LIKE \'%{}%\''.format(title))

        desc = Connection.get_cursor_description(res)

        tasks = []
        for row in res:
            data = Connection.row_to_dict(row, desc)
            task = Task(**data)
            tasks.append(task)

        return tasks
