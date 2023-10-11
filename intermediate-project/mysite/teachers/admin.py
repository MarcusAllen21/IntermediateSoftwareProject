from django.contrib import admin
from .models import Discussion, Reply, Quiz, Grade

admin.site.register(Quiz)
admin.site.register(Grade)
admin.site.register(Discussion)
admin.site.register(Reply)