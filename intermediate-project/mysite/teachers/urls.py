from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    path('', views.index, name='index'),
    path('create_quiz/', views.create_quiz, name='create_quiz'),
    path('quiz_results/<int:quiz_id>/', views.view_quiz_results, name='view_quiz_results'),
    path('quiz/<int:quiz_id>/chart/', views.view_quiz_chart, name='view_quiz_chart'),
    path('create_discussion/', views.create_discussion, name='create_discussion'),
    path('created_quizzes/', views.created_quizzes, name='created_quizzes'),
    path('created_discussions/', views.created_discussions, name='created_discussions'),
    path('questions/<int:quiz_id>/<str:student_username>/', views.questions_view, name='questions'),
]
