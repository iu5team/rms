import datetime
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from django.http.response import Http404, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView
from django.views.generic.detail import DetailView

from app.models import Task, Employee
import app.views.gateway.task_gateway
from app.views import alekseyl
from app.views.gateway.task_gateway import TaskGateway, SpentTimeArguments
from app.views.igor.domain import RMSTask, RMSEmployee


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

    def form_valid(self, form):
        task = TaskGateway(creation_date=form.cleaned_data['creation_date'],
                           finish_date=form.cleaned_data['finish_date'],
                           assignee_id=form.cleaned_data['assignee'].id,
                           status=form.cleaned_data['status'],
                           description=form.cleaned_data['description'],
                           title=form.cleaned_data['title'])
        task.save()
        return HttpResponseRedirect(self.success_url)


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
            tasks = alekseyl.task.Task.find_by_title(query)
        else:
            tasks = Task.objects.all()

        return tasks


class TaskDelete(DeleteView):
    model = Task
    success_url = reverse_lazy('task_list')

    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object and then
        redirects to the success URL.
        """
        task_id = int(self.kwargs['pk'])
        task = TaskGateway.find_by_id(task_id)
        task.delete()
        return HttpResponseRedirect(self.success_url)


class TaskDetail(DetailView):
    model = Task
    template_name_suffix = '_detail'
    object = None

    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get(self.pk_url_kwarg)
        if pk is None:
            raise Http404()

        task = RMSTask.find_by_id(pk)
        task.assignee = RMSEmployee.find_by_id(task.assignee_id)
        context = self.get_context_data(task=task)
        return self.render_to_response(context)


class TaskUpdate(UpdateView):
    model = Task
    fields = ['creation_date', 'finish_date', 'assignee', 'status', 'description', 'title']
    template_name_suffix = '_update'
    success_url = reverse_lazy('task_list')

    def get_form(self, form_class=None):
        form = super(TaskUpdate, self).get_form(form_class)
        datepicker_class = 'datepicker'
        form.fields['creation_date'].widget.attrs.update({'class': datepicker_class})
        form.fields['finish_date'].widget.attrs.update({'class': datepicker_class})
        return form

    def form_valid(self, form):
        task_id = int(self.kwargs['pk'])
        task = TaskGateway.find_by_id(task_id)
        task.creation_date = form.cleaned_data['creation_date']
        task.finish_date = form.cleaned_data['finish_date']
        task.assignee_id = form.cleaned_data['assignee'].id
        task.status = form.cleaned_data['status']
        task.description = form.cleaned_data['description']
        task.title = form.cleaned_data['title']
        task.save()
        return HttpResponseRedirect(self.success_url)


class TasksByDate(View):
    def get(self, request, *args, **kwargs):
        assignee = int(request.GET.get('assignee'))
        date = request.GET.get('date')
        if assignee is None or date is None:
            raise Http404()

        tasks = RMSTask.get_by_date(assignee_id=assignee, date=date)
        context = {'object_list': tasks}
        return render(request, 'api/task_list.html', context=context)


class TaskSpentTime(View):
    def post(self, request, *args, **kwargs):
        task_id = self.kwargs['pk']
        assignee_id = request.POST.get('assignee_id')
        days = request.POST.get('days')

        try:
            args = SpentTimeArguments(task_id, assignee_id, days)
            task = RMSTask.update_wasted_days(args)
        except SpentTimeArguments.BadArguments as e:
            return HttpResponseBadRequest(e.message)

        return redirect(reverse('task_detail', args=[task_id]))
