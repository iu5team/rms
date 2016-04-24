# coding=utf-8

"""
    Модели системы RMS
"""
from __future__ import unicode_literals
import datetime

from django.db import models
from django.utils import timezone


class Position(models.Model):
    """
    Должность
    Поле =- название должности
    """
    title = models.CharField(max_length=100, null=False)

    def __unicode__(self):
        return self.title


class Task(models.Model):
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


class Employee(models.Model):
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
    salary = models.IntegerField(blank=True)

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
