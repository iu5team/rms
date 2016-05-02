# coding=utf-8
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from django.http.response import Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView
from django.views.generic.detail import DetailView

from app.models import Position, Employee, CheckPosTitleService, CheckPosSalaryService


class PositionCreate(CreateView):
    model = Position
    fields = ['title', 'min_salary']
    success_url = reverse_lazy('position_list')

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        self.object = None
        form = self.get_form()

        if form.is_valid():
            try:
                CheckPosTitleService.check(form)
                CheckPosSalaryService.check(form)

                return self.form_valid(form)
            except ValidationError:
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        Position.PosCreate(form.cleaned_data)
        return HttpResponseRedirect(self.success_url)


class PositionDetail(DetailView):
    model = Position
    fields = ['title', 'min_salary']
    template_name_suffix = '_detail'

    def get_context_data(self, **kwargs):
        context = super(PositionDetail, self).get_context_data(**kwargs)
        pk = context['position'].id

        Position.PosRead(pk)
        return context


class PositionUpdate(UpdateView):
    model = Position
    fields = ['title', 'min_salary']
    template_name_suffix = '_update'
    success_url = reverse_lazy('position_list')

    def get_queryset(self):
        pos_id = int(self.kwargs['pk'])

        if pos_id:
            return Position.objects.filter(pk=pos_id)

    def form_valid(self, form):
        pos_id = int(self.kwargs['pk'])
        pos = Position.PosRead(pos_id)
        pos.title = form.cleaned_data['title']
        pos.min_salary = form.cleaned_data['min_salary']
        pos.PosUpdate()
        return HttpResponseRedirect(self.success_url)


class PositionList(ListView):
    model = Position
    template_name = 'positions_list.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(PositionList, self).get_context_data(**kwargs)

        # Add in the query
        query = self.request.GET.get('query')
        context['query'] = query

        return context

    def get_queryset(self):
        query = self.request.GET.get('query')

        if query:
            pos = Position.objects.filter(name__contains=query)
        else:
            pos = Position.objects.all()

        return pos


class PositionDelete(DeleteView):
    model = Position
    success_url = reverse_lazy('position_list')

    def post(self, request, *args, **kwargs):
        id = self.kwargs['pk']
        PositionServices.delete(id)
        return redirect(self.success_url)


class PositionServices():
    @staticmethod
    def delete(position_id):
        pos = Position.PosRead(position_id)
        Employee.objects.filter(position=pos).update(position=None)
        pos.PosDelete()
        return pos
