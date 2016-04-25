import cStringIO
import datetime
from base64 import b64encode

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from app import models
from app.views.alekseyl.model import Model


class Employee(Model):
    data = None

    def __init__(self):
        data = models.Employee()
        Model.__init__(self)

    def update(self):
        pass

    @staticmethod
    def get(pk):
        emp = Employee()
        emp.data = models.Employee.objects.get(pk=pk)

        return emp

    def delete(self):
        pass

    def get_tasks(self):
        return models.Task.objects.filter(assignee=self.data.pk)

    def plot_tasks(self, date_from, date_to):
        tasks = self.get_tasks()

        fig = plt.Figure(facecolor='white')
        ax = fig.add_subplot(111)
        ax.grid(color = 'black', linestyle = ':')

        duration = (date_to - date_from).days

        days = []
        for task in tasks:
            start_date = task.creation_date
            end_date = task.finish_date + datetime.timedelta(1)

            for i in range(duration + 1):
                cur_date = date_from + datetime.timedelta(i)
                if start_date <= cur_date <= end_date:
                    days.append(i)

        dates = []
        for i in range(duration + 1):
            date_name = date_from + datetime.timedelta(i)
            dates.append(str(date_name))

        counts, bins, patches = ax.hist(days, bins=duration, range=(1, duration), histtype='stepfilled')
        ax.set_xticks(bins[:])
        ax.set_xticklabels(dates, rotation=80)
        # ax.set_xticks(ticks)
        ax.set_xlabel('date')

        ax.set_yticks(np.arange(0, counts.max() + 1))
        ax.set_ylabel('tasks')

        ax.set_title('Tasks vs date')
        plt.rcParams["figure.figsize"] = [12, 6]
        fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)

        # fig.autofmt_xdate()
        # formatter = matplotlib.dates.DateFormatter("%b %d")
        # ax.xaxis.set_major_formatter(formatter)

        graphic = cStringIO.StringIO()

        canvas = FigureCanvas(fig)
        canvas.print_png(graphic)

        plot_str = b64encode(graphic.getvalue())
        graphic.close()

        return plot_str
