from django.conf.urls import patterns, url

from project import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^register', views.register, name="register"),
    url(r'^dashboard', views.dashboard, name="dashboard")
)
