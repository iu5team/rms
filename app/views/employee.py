# coding=utf-8
##
# @file
# @brief Обработчики для генерации страниц для CRUD  сотрудника.


from django import forms
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import DetailView, FormView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView
from django.http.response import Http404, HttpResponseBadRequest, HttpResponseRedirect

import app.views.alekseyl.active_record.task
from app.views.alekseyl.domain_model.employee import Employee as AlekseylDomainEmployee
from app.models import Employee, Calendar, Task, EmplNameUpdService, EmplNameCreateService
from app.views import alekseyl
from app.views.alekseyl.domain_model.employee import EmployeeException


class EmployeeCreate(CreateView):
    model = Employee
    fields = ['name', 'manager', 'position', 'salary']
    success_url = reverse_lazy('employee_list')

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()

        if form.is_valid():
            try:
                EmplNameCreateService.check(form)

                return self.form_valid(form)
            except ValidationError:
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        return HttpResponseRedirect(self.success_url)

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

    def post(self, request, *args, **kwargs):
        emp = Employee.EmplRead(self.kwargs['pk'])
        emp.EmplDelete()
        return redirect(self.success_url)


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

        employee = AlekseylDomainEmployee.get(employee_id)
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

    def form_valid(self, form):
        empl_id = int(self.kwargs['pk'])
        empl = Employee.EmplRead(empl_id)
        empl.name = form.cleaned_data['name']
        empl.salary = form.cleaned_data['salary']
        empl.manager = form.cleaned_data['manager']
        empl.position = form.cleaned_data['position']
        if form.is_valid():
            try:
                EmplNameUpdService.checkupd(form, empl)
                return HttpResponseRedirect(self.success_url)
            except ValidationError:
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)


class EmployeeDetail(DetailView):
    model = Employee
    fields = ['name', 'manager', 'position', 'salary']
    template_name_suffix = '_detail'

    def __init__(self, **kwargs):
        super(EmployeeDetail, self).__init__(**kwargs)
        self.implementation = EmployeeUse2(**kwargs)

    def get_context_data(self, **kwargs):
        context = super(EmployeeDetail, self).get_context_data(**kwargs)
        Employee.EmplRead(context['employee'].id)
        self.implementation.get_context_data_impl(context=context)
        return context


class EmployeeImplementation():
    def __init__(self, **kwargs):
        pass

    def get_context_data_impl(self, context):
        pass


class EmployeeUse1(EmployeeImplementation):
    def __init__(self, **kwargs):
        EmployeeImplementation.__init__(self, **kwargs)

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
        EmployeeImplementation.__init__(self, **kwargs)

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
