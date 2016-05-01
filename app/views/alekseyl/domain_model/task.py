from app.views.alekseyl import active_record


class Task(active_record.task.Task):
    def __init__(self, **kwargs):
        super(Task, self).__init__(**kwargs)



