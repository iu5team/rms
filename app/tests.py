import os

import datetime
from pprint import pprint

from django.test import TestCase
from mock import mock

from app.utils.db_utils import Connection
from app.views.alekseyl.domain_model import Task

from app.views.alekseyl import active_record as ar
from app.views.alekseyl.domain_model.task import TaskException
from app.views.gateway.task_gateway import TaskGateway


class TestTaskByBranch(TestCase):
    def setUp(self):
        self.title = None
        ar.Task.find_by_title = staticmethod(lambda title: self.title)

    def test_find_by_title_normal(self):
        self.title = 'normal'
        task = Task.find_by_title(self.title)
        self.assertEqual(task, self.title)

    def test_find_by_title_short(self):
        self.title = 's'
        try:
            Task.find_by_title(self.title)
        except TaskException as e:
            self.assertEqual(e.message, 'Query is too short')
        else:
            self.fail()

    def test_find_by_title_long(self):
        self.title = 's' * 150
        try:
            Task.find_by_title(self.title)
        except TaskException as e:
            self.assertEqual(e.message, 'Query is too long')
        else:
            self.fail()


class TestTaskByBoundaries(TestCase):
    def setUp(self):
        self.title = None
        ar.Task.find_by_title = staticmethod(lambda title: self.title)

    # normal bounds
    def test_find_by_title_normal4(self):
        self.title = 's' * 4
        task = Task.find_by_title(self.title)
        self.assertEqual(task, self.title)

    def test_find_by_title_normal100(self):
        self.title = 's' * 100
        task = Task.find_by_title(self.title)
        self.assertEqual(task, self.title)

    # max error bound
    def test_find_by_title_short(self):
        self.title = 's' * 2
        try:
            Task.find_by_title(self.title)
        except TaskException as e:
            self.assertEqual(e.message, 'Query is too short')
        else:
            self.fail()

    # min error bound
    def test_find_by_title_long(self):
        self.title = 's' * 101
        try:
            Task.find_by_title(self.title)
        except TaskException as e:
            self.assertEqual(e.message, 'Query is too long')
        else:
            self.fail()

    # zero length
    def test_find_by_title_short0(self):
        self.title = ''
        try:
            Task.find_by_title(self.title)
        except TaskException as e:
            self.assertEqual(e.message, 'Query is too short')
        else:
            self.fail()

    # long title
    def test_find_by_title_longInf(self):
        self.title = 's' * 100500
        try:
            Task.find_by_title(self.title)
        except TaskException as e:
            self.assertEqual(e.message, 'Query is too long')
        else:
            self.fail()


class TestTaskGatewayByDU(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestTaskGatewayByDU, cls).setUpClass()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        Connection.DB_PATH = os.path.join(current_dir, '..', 'db.sqlite3')

    def setUp(self):
        t = TaskGateway(
            title='mytitle',
            creation_date=datetime.datetime.now(),
            finish_date=datetime.datetime.now(),
            status='',
            description='123',

        )
        t.save()
        self.task_id = t._id
        self.task = t

    def tearDown(self):
        TaskGateway.find_by_id(self.task_id).delete()

    def test_find_by_title_path1(self):
        title = 'mytitl'
        t = TaskGateway.find_by_title(title, contains=True)
        self.assertEqual(len(t), 1)
        self.assertEqual(t[0].title, self.task.title)

    def test_find_by_title_path2_success(self):
        title = 'mytitle'
        t = TaskGateway.find_by_title(title, contains=False)
        self.assertEqual(len(t), 1)
        self.assertEqual(t[0].title, self.task.title)

    def test_find_by_title_path2_not_found(self):
        title = 'mytitl'
        t = TaskGateway.find_by_title(title, contains=False)
        self.assertEqual(len(t), 0)
