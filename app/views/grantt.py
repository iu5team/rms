from django import forms
from django.shortcuts import render
from django.views.generic import FormView

from app.views.alekseyl.grantt_diagram import GranttDiagram
from app.views.alekseyl.task import Task


class GanttDiagramSettingsForm(forms.Form):
    date_from = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker'}))
    date_to = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker'}))


class GanttDiagramView(FormView):
    template_name = 'app/gantt_diagram_view.html'
    form_class = GanttDiagramSettingsForm

    def form_valid(self, form):
        date_from = form.cleaned_data['date_from']
        date_to = form.cleaned_data['date_to']
        tasks = Task.find(date_from, date_to)

        context = {}
        context['form'] = GanttDiagramSettingsForm(form.data)
        context['graphic'] = GranttDiagram.plot(tasks, date_from, date_to)

        return render(self.request, self.template_name, context)
