from app.views.alekseyl import active_record


class TaskException(Exception):
    pass


class Task(active_record.task.Task):
    def __init__(self, **kwargs):
        super(Task, self).__init__(**kwargs)

    @staticmethod
    def find_by_title(title):
        if len(title) < 3:
            raise TaskException('Query is too short')

        return active_record.task.Task.find_by_title(title)
