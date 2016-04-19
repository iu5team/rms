"""rms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

import app.views

urlpatterns = [
    # url(r'^', app.views.index.IndexView),
    url(r'^employees', app.views.employee.EmployeeList.as_view(), name='employee_list'),
    url(r'^employee', app.views.employee.EmployeeCreate.as_view(), name='employee_create'),
    url(r'^admin/', admin.site.urls),
    url(r'^tasks', app.views.task.TaskList.as_view(), name='task_list'),
    url(r'^(/task/?P<idTask>[0-9]+)/$', app.views.task.TaskDetail.as_view(), name='detail'),
    url(r'^task', app.views.task.TaskCreate.as_view(), name='task_create'),
]
