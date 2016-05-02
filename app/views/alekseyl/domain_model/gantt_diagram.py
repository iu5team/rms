import cStringIO
from base64 import b64encode

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from app.utils.cloneable import Cloneable


class GanttDiagram(Cloneable):
    def __init__(self, title='GanttDiagram', figure_size=(12, 6), background='white'):
        super(GanttDiagram, self).__init__()
        self.title = title
        self.figure_size = figure_size
        self.background = background

    def clone(self):
        new_diagram = GanttDiagram(
            title=self.title,
            figure_size=self.figure_size,
            background=self.background
        )

        return new_diagram

    @staticmethod
    def name_to_color(name):
        import hashlib
        sha = hashlib.sha1(name.encode('utf8'))
        color = sha.hexdigest()[:6]
        return '#' + color

    def plot(self, tasks, date_from, date_to):
        fig = plt.Figure(facecolor=self.background)
        ax = fig.add_subplot(111)
        ax.grid(color='black', linestyle=':')
        ax.set_xlim(date_from, date_to)

        ticks = []
        for i, task in enumerate(tasks):
            start_date = task.creation_date
            end_date = task.finish_date
            duration = (end_date - start_date).days
            assignee = task.name

            ticks.append(start_date)
            ticks.append(end_date)

            ax.barh(i, duration,
                    left=start_date,
                    height=0.1,
                    align='center',
                    color=GanttDiagram.name_to_color(assignee),
                    alpha=0.75,
                    label=assignee)

        ax.set_xticks(ticks)
        ax.set_xlabel('date')

        ax.set_yticklabels(map(lambda task: task.title, tasks))
        ax.set_yticks(np.arange(0, len(tasks)))
        ax.set_ylabel('tasks')

        ax.set_title(self.title)
        plt.rcParams["figure.figsize"] = self.figure_size
        fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.3)

        ax.legend(loc=1)
        fig.autofmt_xdate()
        formatter = matplotlib.dates.DateFormatter("%b %d")
        ax.xaxis.set_major_formatter(formatter)

        # filter legend entries
        handles, labels = ax.get_legend_handles_labels()

        seen_names = set()
        filtered = []
        for pair in zip(handles, labels):
            name = pair[1]
            if name not in seen_names:
                seen_names.add(name)
                filtered.append(pair)

        ax.legend(*zip(*filtered))

        # plot to stream
        graphic = cStringIO.StringIO()

        canvas = FigureCanvas(fig)
        canvas.print_png(graphic)

        plot_str = b64encode(graphic.getvalue())
        graphic.close()

        return plot_str