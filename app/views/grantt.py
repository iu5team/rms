import cStringIO
from base64 import b64encode

import matplotlib
import matplotlib.dates
import matplotlib.pyplot as plt
import numpy as np
from django import forms
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import FormView
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.dates import RRuleLocator

from app.models import Employee, Task


def name_to_color(name):
    import hashlib
    sha = hashlib.sha1(name)
    color = sha.hexdigest()[:6]
    return '#' + color


def plot_gantt_diagram(tasks, date_from, date_to):
    fig = plt.Figure(facecolor='white')
    ax = fig.add_subplot(111)
    ax.grid(color = 'black', linestyle = ':')
    ax.set_xlim(date_from, date_to)

    ticks = []
    for i, task in enumerate(tasks):
        start_date = task.creation_date
        end_date = task.finish_date
        duration = (end_date - start_date).days
        assignee = task.assignee.name

        ticks.append(start_date)
        ticks.append(end_date)

        ax.barh(i, duration,
                left=start_date,
                height=0.1,
                align='center',
                color=name_to_color(assignee),
                alpha = 0.75,
                label=assignee)

    ax.set_xticks(ticks)
    ax.set_xlabel('date')

    ax.set_yticklabels(map(lambda task: task.title, tasks))
    ax.set_yticks(np.arange(0, tasks.count()))
    ax.set_ylabel('tasks')

    ax.set_title('Gantt Diagram')
    plt.rcParams["figure.figsize"] = [12, 6]
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


class GanttDiagramSettingsForm(forms.Form):
    date_from = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker'}))
    date_to = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker'}))


class GanttDiagramView(FormView):
    template_name = 'app/gantt_diagram_view.html'
    form_class = GanttDiagramSettingsForm

    def form_valid(self, form):
        date_from = form.cleaned_data['date_from']
        date_to = form.cleaned_data['date_to']

        context = {}
        context['form'] = GanttDiagramSettingsForm(form.data)

        tasks = Task.objects.filter(~Q(assignee=None) & Q(creation_date__gte=date_from) & Q(finish_date__lte=date_to))
        context['graphic'] = plot_gantt_diagram(tasks, date_from, date_to)

        return render(self.request, self.template_name, context)
