from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("", views.register, name="register"),
    path("login/", views.login_page, name="login_page"),
    path("logout/", views.logout_page, name="logout_page"),
]

print("your mom")