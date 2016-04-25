import cStringIO
from base64 import b64encode

import matplotlib
import matplotlib.dates
import matplotlib.pyplot as plt
import numpy as np
from django import forms
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import FormView
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.dates import RRuleLocator

from app.models import Employee, Task


class GanttDiagramSettingsForm(forms.Form):
    date_from = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker'}))
    date_to = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker'}))


class GanttDiagramView(FormView):
    template_name = 'app/gantt_diagram_view.html'
    form_class = GanttDiagramSettingsForm

    def form_valid(self, form):
        date_from = form.cleaned_data['date_from']
        date_to = form.cleaned_data['date_to']

        context = {}
        context['form'] = GanttDiagramSettingsForm(form.data)

        # TODO
        # tasks = Task.objects.filter(~Q(assignee=None) & Q(creation_date__gte=date_from) & Q(finish_date__lte=date_to))
        # context['graphic'] = plot_gantt_diagram(tasks, date_from, date_to)

        return render(self.request, self.template_name, context)
