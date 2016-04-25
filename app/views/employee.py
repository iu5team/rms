import cStringIO
from base64 import b64encode

import datetime
from datetime import date

from django import forms
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import DetailView, View, FormView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib

from app.models import Employee, Task

import matplotlib.pyplot as plt
import numpy as np


class EmployeeCreate(CreateView):
    model = Employee
    fields = ['name', 'manager', 'position', 'salary']
    success_url = reverse_lazy('employee_list')



class EmployeeList(ListView):
    model = Employee
    template_name = 'employees_list.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(EmployeeList, self).get_context_data(**kwargs)

        # Add in the query
        query = self.request.GET.get('query', '')
        context['query'] = query

        return context

    def get_queryset(self):
        query = self.request.GET.get('query', '')

        if query:
            employees = Employee.objects.filter(name__contains=query)
        else:
            employees = Employee.objects.all()

        return employees


class EmployeeDelete(DeleteView):
    model = Employee
    success_url = reverse_lazy('employee_list')

    def delete(self, request, *args, **kwargs):
        employee = self.get_object()
        Employee.objects.filter(manager=employee).update(manager=None)
        Task.objects.filter(assignee=employee).update(assignee=None)
        return super(EmployeeDelete, self).delete(request, *args, **kwargs)


class EmployeeDetail(DetailView):
    model = Employee
    fields = ['name', 'manager', 'position', 'salary']
    template_name_suffix = '_detail'

    def get_context_data(self, **kwargs):
        context = super(EmployeeDetail, self).get_context_data(**kwargs)
        pk = context['employee'].id

        tasks = Task.objects.filter(assignee=pk)
        context['tasks'] = tasks
        context['tasks_done'] = Task.objects.filter(Q(assignee=pk) & Q(status='done'))
        context['tasks_undone'] = Task.objects.filter(Q(assignee=pk) & ~Q(status='done'))
        context['tasks_dates'] = map(lambda task: task.creation_date, tasks)

        return context


class EmployeePlotSettingsForm(forms.Form):
    date_from = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker'}))
    date_to = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker'}))


def plot_tasks(tasks, date_from, date_to):
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


class EmployeePlotView(FormView):
    template_name = 'app/employee_plot_view.html'
    form_class = EmployeePlotSettingsForm

    def form_valid(self, form):
        date_from = form.cleaned_data['date_from']
        date_to = form.cleaned_data['date_to']

        employee_id = self.kwargs['pk']
        tasks = Task.objects.filter(assignee=employee_id)

        context = {}
        context['form'] = EmployeePlotSettingsForm(form.data)
        context['employee'] = Employee.objects.get(pk=employee_id)
        context['graphic'] = plot_tasks(tasks, date_from, date_to)

        return render(self.request, self.template_name, context)


class EmployeeUpdate(UpdateView):
    model = Employee
    fields = ['name', 'manager', 'position', 'salary']
    template_name_suffix = '_update'
    success_url = reverse_lazy('employee_list')

    def get_queryset(self):
        employee_id = int(self.kwargs['pk'])

        if employee_id:
            return Employee.objects.filter(pk=employee_id)
