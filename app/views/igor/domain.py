from app.views.gateway.employee_gateway import EmployeeGateway
from app.views.gateway.task_gateway import TaskGateway


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
