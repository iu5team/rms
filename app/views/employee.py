from django import forms
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import DetailView, FormView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView

from app.models import Employee, Task
from app.views import alekseyl


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

        employee = alekseyl.employee.Employee.get(employee_id)
        context['employee'] = employee.data
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
