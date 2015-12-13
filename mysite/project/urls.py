from django.conf.urls import patterns, url

from project import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^register', views.register, name="register"),
    url(r'^dashboard', views.dashboard, name="dashboard"),
    url(r'^scrape_data', views.scrape_data, name="scrape_data"),
    url(r'^login_user', views.login_user, name="login_user")
)
