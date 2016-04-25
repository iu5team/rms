import datetime
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from django.http.response import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView
from django.views.generic.detail import DetailView

from app.models import Task, Employee
import app.views.gateway.task_gateway
from app.views.gateway.task_gateway import TaskGateway, SpentTimeArguments


class TaskCreate(CreateView):
    model = Task
    fields = ['creation_date', 'finish_date', 'assignee', 'status', 'description', 'title']
    success_url = reverse_lazy('task_list')

    def get_form(self, form_class=None):
        form = super(TaskCreate, self).get_form(form_class)
        datepicker_class = 'datepicker'
        form.fields['creation_date'].widget.attrs.update({'class': datepicker_class})
        form.fields['finish_date'].widget.attrs.update({'class': datepicker_class})
        return form


class TaskList(ListView):
    model = Task
    template_name = 'tasks_list.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TaskList, self).get_context_data(**kwargs)

        # Add in the query
        query = self.request.GET.get('query')
        context['query'] = query

        return context

    def get_queryset(self):
        query = self.request.GET.get('query')

        if query:
            tasks = Task.objects.filter(title__contains=query)
        else:
            tasks = Task.objects.all()

        return tasks


class TaskDelete(DeleteView):
    model = Task
    success_url = reverse_lazy('task_list')


class TaskDetail(DetailView):
    model = Task
    template_name_suffix = '_detail'
    object = None

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk is None:
            raise Http404()

        task = TaskGateway.find_by_id(pk)
        task.assignee = Employee.get_by_id(task.assignee_id)
        # task.assignee = Employee.objects.filter(pk=task.assignee_id).get()
        context = self.get_context_data(task=task)
        return self.render_to_response(context)


class TaskUpdate(UpdateView):
    model = Task
    fields = ['creation_date', 'finish_date', 'assignee', 'status', 'description', 'title']
    template_name_suffix = '_update'
    success_url = reverse_lazy('task_list')

    def get_queryset(self):
        task_id = int(self.kwargs['pk'])

        if task_id:
            return Task.objects.filter(pk=task_id)

    def get_form(self, form_class=None):
        form = super(TaskUpdate, self).get_form(form_class)
        datepicker_class = 'datepicker'
        form.fields['creation_date'].widget.attrs.update({'class': datepicker_class})
        form.fields['finish_date'].widget.attrs.update({'class': datepicker_class})
        return form


class TasksByDate(View):
    def get(self, request, *args, **kwargs):
        assignee = int(request.GET.get('assignee'))
        date = request.GET.get('date')
        if assignee is None or date is None:
            raise Http404()

        context = {'object_list': Task.objects.filter(assignee_id=assignee,
                                                      creation_date=date)}
        return render(request, 'api/task_list.html', context=context)


class TaskSpentTime(View):
    def post(self, request, *args, **kwargs):
        task_id = self.kwargs['pk']
        assignee_id = request.POST.get('assignee_id')
        days = request.POST.get('days')

        try:
            args = SpentTimeArguments(task_id, assignee_id, days)
            task = TaskGateway.update_wasted_days(args)
        except SpentTimeArguments.BadArguments as e:
            return HttpResponseBadRequest(e.message)

        return redirect(reverse('task_detail', args=[task_id]))
