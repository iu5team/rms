# coding=utf-8

##
# @file
# @brief Обработчики для генерации страниц для CRUD должности.
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

##
# @brief Класс-обработчик запроса на создание новой должности
#
# Забирает данные с формы с помощью POST-запроса, проверяет форму и в случае успеха
# создает запись в таблице.

class PositionCreate(CreateView):
    model = Position
    fields = ['title', 'min_salary']
    success_url = reverse_lazy('position_list')

    ##
    # @brief перегруженный метод post
    #
    # Запускает проверки для формы, обращаясь к слою служб.
    # В случае успешного завершения всех проверок создает запись в таблице с помощью методов класса Position в models.
    # @param request - HTTP-запрос
    # @return HTML-страница со списком всех имеющихся должностей
    #
    #
    def post(self, request, *args, **kwargs):

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

    ##
    # @brief Класс-обработчик запроса на обзор должности
    #
class PositionDetail(DetailView):
    model = Position
    fields = ['title', 'min_salary']
    template_name_suffix = '_detail'

    ##
    # @brief Возвращает контекст с запрошенной должностью.
    #
    # Вызывет PosRead в Position используя паттерн активной записи
    # @return HTML-страница выбранной должности.
    def get_context_data(self, **kwargs):
        context = super(PositionDetail, self).get_context_data(**kwargs)
        pk = context['position'].id

        Position.PosRead(pk)
        return context


##
# @brief Класс-обработчик запроса на обновление должности
#
class PositionUpdate(UpdateView):
    model = Position
    fields = ['title', 'min_salary']
    template_name_suffix = '_update'
    success_url = reverse_lazy('position_list')

    def get_queryset(self):
        pos_id = int(self.kwargs['pk'])

        if pos_id:
            return Position.objects.filter(pk=pos_id)
    ##
    # @brief Метод проверки формы на правильность заполнения.
    #
    # Проверяет форму, полученную от пользователя на корректность заполнения,
    # в случае успешной проверки вызывает PosUpdate в Position.
    #
    # @return Список всех должностей
    def form_valid(self, form):
        pos_id = int(self.kwargs['pk'])
        pos = Position.PosRead(pos_id)
        pos.title = form.cleaned_data['title']
        pos.min_salary = form.cleaned_data['min_salary']
        if form.is_valid():
            try:
                CheckPosTitleService.check(form)
                CheckPosSalaryService.check(form)
                pos.PosUpdate()
                return HttpResponseRedirect(self.success_url)
            except ValidationError:
                return self.form_invalid(form)
        else:
            return self.form_invalid(form)

##
# @brief Класс-обработчик запроса на вывод всех должностей, имеющихся в системе
#
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

##
# @brief Класс-обработчик запроса на удаление выбранной должности.
#
class PositionDelete(DeleteView):
    model = Position
    success_url = reverse_lazy('position_list')

    ##
    # @brief Метод для удаления выбранной должности.
    #
    # Получает выбранную должность по первичному ключу (pk) и удаляет ее с помощью метода PosDelete в Position.

    def post(self, request, *args, **kwargs):
        pos = Position.PosRead(self.kwargs['pk'])
        pos.PosDelete()
        return redirect(self.success_url)