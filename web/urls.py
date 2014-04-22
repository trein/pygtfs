from django.conf.urls import patterns, url

from web import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^bus/lines/$', views.bus_lines, name='bus_lines'),
    # url(r'^articles/(?P<pk>\d+)/$', views.ShowView.as_view(), name='detail'),
)