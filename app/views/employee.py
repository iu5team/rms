from django import forms
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.views.generic import DetailView, FormView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView

import app.views.alekseyl.active_record.task
from app.models import Employee, Calendar, Task
from app.views import alekseyl
from app.views.alekseyl.domain_model.employee import EmployeeException


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
            try:
                employees = app.views.alekseyl.domain_model.employee.Employee.find_by_name(query)
            except EmployeeException:
                employees = []
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


class EmployeePlotSettingsForm(forms.Form):
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
        context['form'] = form

        employee = app.views.alekseyl.active_record.employee.Employee.get(employee_id)
        context['employee'] = employee
        context['graphic'] = employee.plot_tasks(date_from, date_to)

        return render(self.request, self.template_name, context)


class EmployeeUpdate(UpdateView):
    model = Employee
    fields = ['name', 'manager', 'position', 'salary']
    template_name_suffix = '_update'
    success_url = reverse_lazy('employee_list')

    # demonstration purpose method
    def change_name(self):
        emp = alekseyl.active_record.Employee.find_by_id(id)
        emp.name = self.kwargs['name']
        emp.update()

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
        self.implementation = EmployeeUse2(**kwargs)

    def get_context_data(self, **kwargs):
        context = super(EmployeeDetail, self).get_context_data(**kwargs)
        self.implementation.get_context_data_impl(context=context)
        return context


class EmployeeImplementation():
    def __init__(self, **kwargs):
        pass

    def get_context_data_impl(self, context):
        pass


class EmployeeUse1(EmployeeImplementation):
    def __init__(self, **kwargs):
        pass

    def get_context_data_impl(self, context):
        pk = context['employee'].id

        tasks = app.views.alekseyl.active_record.task.Task.find_by_assignee(pk)
        context['tasks'] = tasks
        context['tasks_done'] = filter(lambda task: task.status == 'done', tasks)
        context['tasks_undone'] = filter(lambda task: task.status != 'done', tasks)
        context['tasks_dates'] = map(lambda task: task.creation_date, tasks)
        return context


class EmployeeUse2(EmployeeImplementation):
    def __init__(self, **kwargs):
        pass

    def get_context_data_impl(self, context):
        pk = context['employee'].id

        tasks = app.views.alekseyl.active_record.task.Task.find_by_assignee(pk)
        context['tasks'] = tasks
        context['tasks_done'] = filter(lambda task: task.status == 'done', tasks)
        context['tasks_undone'] = filter(lambda task: task.status != 'done', tasks)
        context['tasks_dates'] = map(lambda task: task.creation_date, tasks)

        vacation_dates = Calendar.objects.filter(person_id=pk, type=Calendar.vyh)
        medical_dates = Calendar.objects.filter(person_id=pk, type=Calendar.bol)
        context['vacation_dates'] = map(lambda entry: (entry.id, entry.date), vacation_dates)
        context['medical_dates'] = map(lambda entry: (entry.id, entry.date), medical_dates)

        return context
