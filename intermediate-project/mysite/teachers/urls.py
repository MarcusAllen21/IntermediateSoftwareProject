from django.urls import path

from . import views

app_name = "teachers"

urlpatterns = [
    path("", views.index, name="index"),
    path("create_quiz/", views.create_quiz, name="create_quiz"),
]