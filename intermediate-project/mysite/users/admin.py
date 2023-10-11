from django.contrib import admin
from .models import Account

#lets you see accounts in admin panel
admin.site.register(Account)
