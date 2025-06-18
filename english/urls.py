from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='eng_dashboard'),
    path('task/', views.quiz_task, name='eng_task'),
    path('check-word/<str:word>', views.check_eng_word, name='check_eng_word'),
    path('add-word/', views.add_word, name='add_eng_word'),
    path('delete-word/', views.delete_word, name='delete_eng_word'),
    path('search-word/', views.search_word, name='search_eng_word'),
    path('get-translations/', views.get_translations_check_word, name='get_eng_trans_check'),
]