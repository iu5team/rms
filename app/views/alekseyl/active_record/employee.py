from app.views.alekseyl.model import Model

from app.utils.db_utils import *
from app.views.alekseyl.active_record.task import Task


class Employee(Model):
    id = None
    name = None
    position_id = None
    salary = None
    manager_id = None

    def __init__(self, **kwargs):
        super(Employee, self).__init__(**kwargs)

    def update(self):
        pass

    @staticmethod
    def get(pk):
        conn = Connection.get_connection()
        cursor = conn.cursor()

        res = cursor.execute('SELECT * FROM app_employee WHERE `id` = ? LIMIT 1', pk)
        desc = Connection.get_cursor_description(res)
        row = res.fetchone()
        data = Connection.row_to_dict(row, desc)

        emp = Employee(**data)
        return emp

    @staticmethod
    def find_by_name(name):
        conn = Connection.get_connection()
        cursor = conn.cursor()

        res = cursor.execute(
            'SELECT * FROM app_employee as e ' +
            'WHERE name LIKE \'%{}%\''.format(name))

        desc = Connection.get_cursor_description(res)

        employees = []
        for row in res:
            data = Connection.row_to_dict(row, desc)
            employee = Task(**data)
            employees.append(employee)

        return employees

    def delete(self):
        pass

    def get_tasks(self, date_from, date_to):
        return Task.find(date_from, date_to, self.id)
