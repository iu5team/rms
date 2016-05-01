from app.views.gateway.employee_gateway import EmployeeGateway
from app.views.gateway.task_gateway import TaskGateway


class RMSTask(TaskGateway):
    @classmethod
    def update_wasted_days(cls, args):
        """
        :type args: SpentTimeArguments
        """
        task = cls.find_by_id(args.task_id)
        task.wasted_days = args.days
        task.save()
        return task

    @classmethod
    def get_by_date(cls, assignee_id, date):
        tasks = cls.find_by_fields(assignee_id=assignee_id, creation_date=date)
        return tasks


class RMSEmployee(EmployeeGateway):
    pass
