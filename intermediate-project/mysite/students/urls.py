from django.urls import path

from . import views

app_name = "students"

urlpatterns = [
    path("", views.index, name="index"),
    path("submit_quiz/<str:id>/", views.submit_quiz, name="submit_quiz"),
    path("create_discussion/", views.create_discussion, name="create_discussion"),
]