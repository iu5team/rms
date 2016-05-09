# coding=utf-8

##
# @file
# @brief Описание модели предметной области. Содержит классы сущностей предметной области
# @mainpage Система управления ресурсами (Resource Management System - RMS).
# @authors
# Латкин И. Леонтьев Л. Гамазов И.
# @date 21.04.2016
# @version 1.2
# @par Примеры документации:
# - @ref models.py - Классы сущностей предметной области
# - @ref utils/cloneable.py - Базовый класс для паттерна Прототип
# - @ref views/alekseyl/domain_model/gantt_diagram.py - Диaграмма Ганта
# - @ref views/gateway/gateway.py - Шлюз записи


from __future__ import unicode_literals

import abc
import datetime
from app.utils.db_utils import *
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


##
# @brief Класс описания должности ( для CRUD должности)
#
# Должность
# Поля
# - название должности
# - Мин. зарплата
class Position(models.Model, AbstractModel):
    ## Название должности
    title = models.CharField(max_length=100, null=False)
    ## Минимальная зарплата
    min_salary = models.IntegerField(null=False, validators=[])

    def __unicode__(self):
        return self.title

    @classmethod
    ##
    # @brief Create должности для активной записи.
    # @param fields - поля для добавления в таблицу
    #
    def PosCreate(cls, fields):
        title = fields.get('title')
        min_salary = fields.get('min_salary')

        conn = Connection.get_connection()
        conn.execute("""INSERT INTO {} (`title`, `min_salary`) VALUES (?, ?)""".format(cls._meta.db_table),
                     (title, min_salary))
        conn.commit()

    @staticmethod
    ##
    # @brief Read должности для активной записи.
    # @param pos_id - id читаемой записи

    def PosRead(pos_id):
        conn = Connection.get_connection()
        cursor = conn.cursor()

        res = cursor.execute('SELECT * FROM app_position WHERE `id` = ? LIMIT 1', [pos_id])
        desc = Connection.get_cursor_description(res)
        row = res.fetchone()
        data = Connection.row_to_dict(row, desc)

        pos = Position(**data)
        return pos

    ##
    # @brief Update должности для активной записи.
    # Обновляет поля записи, для которой был вызван.

    def PosUpdate(self):
        conn = Connection.get_connection()
        update_sql = []
        update_args = []
        for attr in ['title', 'min_salary']:
            update_sql.append('{} = ?'.format(attr))
            update_args.append(getattr(self, attr))
        update_sql = ','.join(update_sql)
        update_args.append(self.id)

        conn.execute("""
              UPDATE {} SET {} WHERE `id` = ?
            """.format(self._meta.db_table, update_sql),
                     update_args)
        conn.commit()

    ##
    # @brief Delete должности для активной записи.
    # Удаляет запись для которой был вызван.
    def PosDelete(self):
        conn = Connection.get_connection()
        conn.execute("DELETE FROM {} WHERE `id` = ?".format(self._meta.db_table), [self.id])
        conn.commit()


class PosService:
    def __init__(self):
        pass

    @staticmethod
    @abc.abstractmethod
    def check(position_form):
        pass


class CheckPosTitleService(PosService):
    @staticmethod
    def check(position_form):
        if len(position_form.cleaned_data['title']) < 4:
            error = u'Слишком короткое название должности!'
            position_form.add_error('title', error)
            raise ValidationError(error)


class CheckPosSalaryService(PosService):
    @staticmethod
    def check(position_form):
        if position_form.cleaned_data['min_salary'] < 6500:
            error = u'Слишком маленькая зарплата!'
            position_form.add_error('min_salary', error)
            raise ValidationError(error)


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
        @param emloyee: Сотрудник (класс Employee)
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

    def EmplCreate(self):
        conn = Connection.get_connection()
        update_sql = []
        update_args = []
        for attr in ['name', 'manager_id', 'position_id', 'salary']:
            update_sql.append('{} = ?'.format(attr))
            update_args.append(getattr(self, attr))
        update_sql = ','.join(update_sql)
        conn.execute("""INSERT INTO {} (`name`, `manager_id`, `position_id`, `salary`) VALUES (?, ?, ? ,?)""".format(
            self._meta.db_table, update_sql),
            update_args)
        conn.commit()

    ##
    # @brief Read должности для активной записи.
    # @param pos_id - id читаемой записи
    @staticmethod
    def EmplRead(empl_id):
        conn = Connection.get_connection()
        cursor = conn.cursor()

        res = cursor.execute('SELECT * FROM app_employee WHERE `id` = ? LIMIT 1', [empl_id])
        desc = Connection.get_cursor_description(res)
        row = res.fetchone()
        data = Connection.row_to_dict(row, desc)

        empl = Employee(**data)
        return empl

    ##
    # @brief Update должности для активной записи.
    # Обновляет поля записи, для которой был вызван.
    def EmplUpdate(self):
        conn = Connection.get_connection()
        update_sql = []
        update_args = []
        for attr in ['name', 'manager_id', 'position_id', 'salary']:
            update_sql.append('{} = ?'.format(attr))
            update_args.append(getattr(self, attr))
        update_sql = ','.join(update_sql)
        update_args.append(self.id)

        conn.execute("""
              UPDATE {} SET {} WHERE `id` = ?
            """.format(self._meta.db_table, update_sql),
                     update_args)
        conn.commit()

    ##
    # @brief Delete должности для активной записи.
    # Удаляет запись для которой был вызван.
    def EmplDelete(self):
        conn = Connection.get_connection()
        conn.execute("DELETE FROM {} WHERE `id` = ?".format(self._meta.db_table), [self.id])
        conn.commit()

    def __unicode__(self):
        return "{}".format(self.name)


class EmployeeService:
    def __init__(self):
        pass

    @staticmethod
    @abc.abstractmethod
    def check(employee_form):
        pass

    @staticmethod
    @abc.abstractmethod
    def checkupd(employee_form, employee):
        pass


class EmplNameCreateService(EmployeeService):
    @staticmethod
    def check(employee_form):
        if len(employee_form.cleaned_data['name']) < 4:
            error = u'Слишком короткое имя!'
            employee_form.add_error('name', error)
            raise ValidationError(error)
        else:
            EmplSalaryCreateService.check(employee_form)


class EmplSalaryCreateService(EmployeeService):
    @staticmethod
    def check(employee_form):
        if employee_form.cleaned_data['salary'] < 6500:
            error = u'Слишком маленькая зарплата!'
            employee_form.add_error('salary', error)
            raise ValidationError(error)
        else:
            employee = Employee(name=employee_form.cleaned_data['name'],
                                manager_id=employee_form.cleaned_data['manager'].id,
                                position_id=employee_form.cleaned_data['position'].id,
                                salary=employee_form.cleaned_data['salary'])
            employee.EmplCreate()


class EmplNameUpdService(EmployeeService):
    @staticmethod
    def checkupd(employee_form, employee):
        if len(employee_form.cleaned_data['name']) < 4:
            error = u'Слишком короткое имя!'
            employee_form.add_error('name', error)
            raise ValidationError(error)
        else:
            empl = employee
            EmplSalaryUpdService.checkupd(employee_form, empl)

    @staticmethod
    def check(employee_form):
        pass


class EmplSalaryUpdService(EmployeeService):
    @staticmethod
    def checkupd(employee_form, employee):
        if employee_form.cleaned_data['salary'] < 6500:
            error = u'Слишком маленькая зарплата!'
            employee_form.add_error('salary', error)
            raise ValidationError(error)
        else:
            empl = employee
            empl.EmplUpdate()

    @staticmethod
    def check(employee_form):
        pass


class Calendar(models.Model):
    """
    Отметки о выходных и больничных
    """
    vyh = 'выходной'
    bol = 'больничный'
    day_coice = ((vyh, 'выходной'), (bol, 'больничный'))
    person = models.ForeignKey(Employee, null=False)
    date = models.DateField(null=False)
    type = models.CharField(max_length=10, null=False, choices=day_coice, default=vyh)

    def set_person(self, person):
        self.person = person
        self.save()
        return self
