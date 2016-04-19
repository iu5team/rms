from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView
from django.views.generic.detail import DetailView

from app.models import Task


class TaskCreate(CreateView):
    model = Task
    fields = ['creationDate', 'finishDate', 'assignee', 'status', 'description', 'title']
    success_url = reverse_lazy('task_list')


class TaskList(ListView):
    model = Task
    template_name = 'tasks_list.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TaskList, self).get_context_data(**kwargs)

        # Add in the query
        query = self.request.GET.get('query', '')
        context['query'] = query

        return context

    def get_queryset(self):
        query = self.request.GET.get('query', '')

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
    fields = ['creationDate', 'finishDate', 'assignee', 'status', 'description', 'title']
    template_name_suffix = '_detail'

    def get_context_data(self, **kwargs):
        context = super(TaskDetail, self).get_context_data(**kwargs)

        query = self.request.GET.get('query', '')
        context['query'] = query

        return context

    def get_queryset(self):
        query = self.request.GET.get('query', '')

        if query:
            tasks = Task.objects.filter(pk=query)
        else:
            tasks = Task.objects.all()

        return tasks

