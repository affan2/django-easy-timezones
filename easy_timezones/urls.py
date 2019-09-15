from django.conf.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^without_tz/$', views.without_tz, name="without_tz"),
    re_path(r'^with_tz/$', views.with_tz, name="with_tz"),
]
