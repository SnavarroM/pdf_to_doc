from django.urls import path
from .views import index
from django.urls import path
from . import views


urlpatterns = [
    path('', index,name='index'),
    path('get_progress/', views.get_progress, name='get_progress')
]