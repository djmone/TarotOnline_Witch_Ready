from django.contrib import admin
from .models import Profile
@admin.register(Profile)
class PAdmin(admin.ModelAdmin): list_display=('user','free_uses_remaining','credits')
