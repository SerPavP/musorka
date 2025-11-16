from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('practice/', views.practice, name='practice'),
    path('theory/', views.theory, name='theory'),
]



