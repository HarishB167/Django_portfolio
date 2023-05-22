from django.urls import include, path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('sync/', views.sync, name="sync")
]