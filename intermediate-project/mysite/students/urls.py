from django.urls import path

from . import views

app_name = "students"

urlpatterns = [
    path("", views.index, name="index"),
    path('create_discussion/', views.create_discussion, name='create_discussion'),
    path('created_discussions/', views.discussions, name='discussions'),
    path('quizzes/<int:quiz_id>/', views.quizzes, name='quizzes'),
    path('grades/', views.grades, name='grades'),
]