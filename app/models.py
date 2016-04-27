# coding=utf-8

"""
    Модели системы RMS
"""
from __future__ import unicode_literals

import abc
import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class AbstractModelsMediator:
    def __init__(self):
        pass

    @abc.abstractmethod
    def get_by_id(self, id, model):
        raise NotImplementedError()


class ModelsMediator(AbstractModelsMediator):
    def __init__(self):
        AbstractModelsMediator.__init__(self)

    def get_by_id(self, id, model):
        return model.objects.filter(pk=id).get()


MEDIATOR = ModelsMediator()


class AbstractModel(object):
    mediator = MEDIATOR

    def __init__(self, *args, **kwargs):
        super(AbstractModel, self).__init__()

    @classmethod
    def get_by_id(cls, id):
        return cls.mediator.get_by_id(id, cls)


def validate_salary(value):
    if value < 6500:
        raise ValidationError('Слишком маленькая зарплата!')


class Position(models.Model, AbstractModel):
    """
    Должность
    Поле =- название должности
    Мин. зарплата
    """

    title = models.CharField(max_length=100, null=False)
    min_salary = models.IntegerField(null=False, validators=[validate_salary])

    def __unicode__(self):
        return self.title


class Task(models.Model, AbstractModel):
    """
    Задача
    Поля:
        - Дата начала
        - Дата окончания
        - Ответственный сотрудник
        - Статус
        - Описание
        - Название
    """
    creation_date = models.DateField(blank=True)
    finish_date = models.DateField(blank=True)
    assignee = models.ForeignKey('Employee', null=True, blank=True)
    status = models.CharField(max_length=45)
    description = models.CharField(max_length=255)
    title = models.CharField(max_length=20)
    wasted_days = models.IntegerField(null=True)

    def set_assignee(self, employee):
        """Метод установки ответственного
        :param emloyee: Сотрудник (класс Employee)
        """
        self.assignee = employee
        self.save()
        return self

    def __unicode__(self):
        return self.title


class Employee(models.Model, AbstractModel):
    """
        Модель сотрудника

        Поля:
            - name - ФИО сотрудника
            - manager - Ссылка на руководителя
            - position - Ссылка на должность сотрудника
            - salary - ставка/зарплата
    """
    name = models.CharField(max_length=100, null=False)
    manager = models.ForeignKey('Employee', null=True, blank=True)
    position = models.ForeignKey(Position, null=True)
    salary = models.IntegerField(blank=True, validators=[validate_salary])

    def set_manager(self, manager):
        """
        Метод установки руководителя

        :param manager: Руководитель (класс Employee)
        """
        self.manager = manager
        self.save()
        return self

    def set_position(self, position):
        """
        Метод установки должности

        :param position: Должность (класс Position)
        """
        self.position = position
        self.save()
        return self

    def __unicode__(self):
        return "{}".format(self.name)


class Calendar(models.Model):
    """
    Отметки о выходных и больничных
    """
    person = models.ForeignKey(Employee, null=False)
    date = models.DateField(null=False)
    type = models.CharField(max_length=10, null=False)

    def set_person(self, person):
        self.person = person
        self.save()
        return self

