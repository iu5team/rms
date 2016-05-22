from app.views.alekseyl import active_record


class TaskException(Exception):
    pass


class Task(active_record.task.Task):
    @staticmethod
    def find_by_title(title):
        if len(title) < 3:
            raise TaskException('Query is too short')

        if len(title) > 100:
            raise TaskException('Query is too long')

        return active_record.task.Task.find_by_title(title)
