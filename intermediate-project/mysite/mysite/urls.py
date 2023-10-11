
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("", include("users.urls")),
    path("students/", include("students.urls")),
    path("teachers/", include("teachers.urls")),
    path("admin/", admin.site.urls),
]
