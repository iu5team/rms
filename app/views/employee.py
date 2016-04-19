from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView

from app.models import Employee


class EmployeeCreate(CreateView):
    model = Employee
    fields = ['name', 'manager', 'position']
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


class TaskDelete(DeleteView):
    model = Employee
    success_url = reverse_lazy('employee_list')