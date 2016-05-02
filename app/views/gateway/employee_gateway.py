import datetime

from app.views.gateway.gateway import Gateway, Connection


class EmployeeGateway(Gateway):
    TABLE_NAME = 'app_employee'
    FIELDS = {
        'id',
        'name',
        'position_id',
        'salary',
        'manager_id'
    }
