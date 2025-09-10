from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='hist_dashboard'),
    path('task/', views.quiz_task, name='hist_task'),
    path('add-date/', views.add_hist_date, name='add_hist_date'),
    path('delete-date/', views.delete_hist_date, name='delete_hist_date'),
    path('search-date/', views.search_hist_date, name='search_hist_date'),
]