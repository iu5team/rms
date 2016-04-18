from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import View
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from app.models import Employee


class EmployeeCreate(CreateView):
    model = Employee
    fields = ['last_name', 'first_name', 'manager', 'position']
    success_url = reverse_lazy('employee_list')


class EmployeeList(ListView):
    model = Employee
    template_name = 'employees_list.html'
