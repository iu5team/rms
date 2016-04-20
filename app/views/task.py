from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView
from django.views.generic.detail import DetailView

from app.models import Task


class TaskCreate(CreateView):
    model = Task
    fields = ['creationDate', 'finishDate', 'assignee', 'status', 'description', 'title']
    success_url = reverse_lazy('task_list')

    def get_form(self, form_class=None):
        form = super(TaskCreate, self).get_form(form_class)
        datepicker_class = 'datepicker'
        form.fields['creationDate'].widget.attrs.update({'class': datepicker_class})
        form.fields['finishDate'].widget.attrs.update({'class': datepicker_class})
        return form


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

    def get_queryset(self):
        task_id = int(self.kwargs['pk'])

        if task_id:
            return Task.objects.filter(pk=task_id)


class TaskUpdate(UpdateView):
    model = Task
    fields = ['creationDate', 'finishDate', 'assignee', 'status', 'description', 'title']
    template_name_suffix = '_update'
    success_url = reverse_lazy('task_list')

    def get_queryset(self):
        task_id = int(self.kwargs['pk'])

        if task_id:
            return Task.objects.filter(pk=task_id)
