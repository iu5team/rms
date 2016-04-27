# coding=utf-8
from django import forms
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from django.http.response import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView
from django.views.generic.detail import DetailView

from app.models import Calendar, Employee


class CalendarCreate(CreateView):
    model = Calendar
    fields = ['date', 'type']

    def get_form(self, form_class=None):
        form = super(CalendarCreate, self).get_form(form_class)
        datepicker_class = 'datepicker'
        form.fields['date'].widget.attrs.update({'class': datepicker_class})
        return form

    def form_valid(self, form):
        employee = Employee.get_by_id(self.kwargs['pk'])
        form.instance.person = employee
        return super(CalendarCreate, self).form_valid(form)

    def get_success_url(self):
        id = int(self.kwargs['pk'])
        self.success_url = reverse_lazy('employee_detail', args=[id])
        return super(CalendarCreate, self).get_success_url()


class CalendarDetail(DetailView):
    model = Calendar
    fields = ['person', 'date', 'type']
    template_name_suffix = '_detail'

    def get_context_data(self, **kwargs):
        context = super(CalendarDetail, self).get_context_data(**kwargs)
        return context


class CalendarUpdate(UpdateView):
    model = Calendar
    fields = ['person', 'date', 'type']
    template_name_suffix = '_update'
    success_url = reverse_lazy('employee_list')  # надо выводить на страницу сотрудника, для которого добавляли!

    def get_queryset(self):
        cal_id = int(self.kwargs['pk'])

        if cal_id:
            return Calendar.objects.filter(pk=cal_id)


class CalendarDelete(DeleteView):
    model = Calendar
    success_url = reverse_lazy('employee_list')  # надо выводить на страницу сотрудника, для которого добавляли!
