from app.views.alekseyl.active_record.model import Model

from app.utils.db_utils import *
from app.views.alekseyl.active_record.task import Task


class Employee(Model):
    __table__ = 'app_employee'

    def __init__(self, **kwargs):
        self.id = None
        self.name = None
        self.position_id = None
        self.salary = None
        self.manager_id = None

        super(Employee, self).__init__(**kwargs)

    @classmethod
    def find_by_name(cls, name):
        conn = Connection.get_connection()
        cursor = conn.cursor()

        res = cursor.execute(
            'SELECT * FROM app_employee as e ' +
            'WHERE name LIKE \'%{}%\''.format(name))

        desc = Connection.get_cursor_description(res)

        employees = []
        for row in res:
            data = Connection.row_to_dict(row, desc)
            employee = cls(**data)
            employees.append(employee)

        return employees

    def get_tasks(self, date_from, date_to):
        return Task.find(date_from, date_to, self.id)
