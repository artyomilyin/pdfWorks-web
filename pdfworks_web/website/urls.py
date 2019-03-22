from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('split/', views.split, name='split'),
    path('merge/', views.merge, name='merge'),
    path('offline/', views.offline, name='offline'),
]
