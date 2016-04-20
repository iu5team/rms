from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView

from app.models import Employee, Task


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

    def get_queryset(self):
        employee_id = int(self.kwargs['pk'])

        if employee_id:
            return Employee.objects.filter(pk=employee_id)


class EmployeeUpdate(UpdateView):
    model = Employee
    fields = ['name', 'manager', 'position', 'salary']
    template_name_suffix = '_update'
    success_url = reverse_lazy('employee_list')

    def get_queryset(self):
        employee_id = int(self.kwargs['pk'])

        if employee_id:
            return Employee.objects.filter(pk=employee_id)
