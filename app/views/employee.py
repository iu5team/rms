import copy

from django import forms
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import DetailView, FormView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView

from app.models import Employee, Task, Calendar
from app.utils.cloneable import ICloneable
from app.views import alekseyl
import app.views.alekseyl.task


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
        query = self.request.GET.get('query')
        context['query'] = query

        return context

    def get_queryset(self):
        query = self.request.GET.get('query')

        if query:
            employees = alekseyl.employee.Employee.find_by_name(query)
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


class EmployeePlotSettingsForm(forms.Form, ICloneable):
    date_from = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker'}))
    date_to = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker'}))


class EmployeePlotView(FormView):
    template_name = 'app/employee_plot_view.html'
    form_class = EmployeePlotSettingsForm

    def form_valid(self, form):
        date_from = form.cleaned_data['date_from']
        date_to = form.cleaned_data['date_to']

        employee_id = self.kwargs['pk']

        context = {}
        context['form'] = form.clone()

        employee = alekseyl.employee.Employee.get(employee_id)
        context['employee'] = employee
        context['graphic'] = employee.plot_tasks(date_from, date_to)

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


class EmployeeDetail(DetailView):
    model = Employee
    fields = ['name', 'manager', 'position', 'salary']
    template_name_suffix = '_detail'

    def __init__(self, **kwargs):
        super(EmployeeDetail, self).__init__(**kwargs)
        self.implementation = EmployeeImplementation(**kwargs)

    def get_context_data(self, **kwargs):
        context = super(EmployeeDetail, self).get_context_data(**kwargs)
        self.implementation.get_context_data(context=context)
        return context


class EmployeeImplementation():
    def __init__(self, **kwargs):
        pass

    def get_context_data(self, context):
        pk = context['employee'].id

        tasks = alekseyl.task.Task.find_by_assignee(pk)
        context['tasks'] = tasks
        context['tasks_done'] = filter(lambda task: task.status == 'done', tasks)
        context['tasks_undone'] = filter(lambda task: task.status != 'done', tasks)
        context['tasks_dates'] = map(lambda task: task.creation_date, tasks)

        vacation_dates = Calendar.objects.filter(person_id=pk, type=Calendar.vyh)
        medical_dates = Calendar.objects.filter(person_id=pk, type=Calendar.bol)
        context['vacation_dates'] = map(lambda entry: entry.date, vacation_dates)
        context['medical_dates'] = map(lambda entry: entry.date, medical_dates)

        return context
