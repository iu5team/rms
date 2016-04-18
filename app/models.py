# coding=utf-8

"""
    Модели системы RMS
"""

from __future__ import unicode_literals

from django.db import models


class Position(models.Model):
    """
    Должность
    Поле =- название должности
    """
    title = models.CharField(max_length=100, null=False)

    def __unicode__(self):
        return self.title


class Employee(models.Model):
    """
        Модель сотрудника

        Поля:
            - name - ФИО сотрудника
            - manager - Ссылка на руководителя
            - position - Ссылка на должность сотрудника
    """
    name = models.CharField(max_length=100, null=False)
    manager = models.ForeignKey('Employee', null=True, blank=True)
    position = models.ForeignKey(Position, null=True)

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
