# coding=utf-8
from __future__ import unicode_literals

from django.db import models

"""@package models
   Модели системы RMS
"""


class Position(models.Model):
    """Модель должностей

    Поля:
        - title - Название должности
    """
    title = models.CharField(max_length=100, null=False)


class Employee(models.Model):
    """Модель сотрудника

        Поля:
            - last_name - Фамилия сотрудника
            - first_name - Имя сотрудника
            - manager - Ссылка на руководителя
            - position - Ссылка на должность сотрудника
    """
    last_name = models.CharField(max_length=100, null=False)
    first_name = models.CharField(max_length=100, null=False)
    manager = models.ForeignKey('Employee', null=True)
    position = models.ForeignKey(Position, null=True)

    def set_manager(self, manager):
        """Метод установки руководителя

        :param manager: Руководитель (класс Employee)
        """
        self.manager = manager
        self.save()
        return self

    def set_position(self, position):
        """Метод установки должности

        :param position: Должность (класс Position)
        """
        self.position = position
        self.save()
        return self
