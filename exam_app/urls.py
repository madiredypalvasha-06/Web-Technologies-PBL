from django.urls import path
from . import views

urlpatterns = [
    path('exam/', views.start_exam, name='start_exam'),
]
