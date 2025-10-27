
from django.contrib import admin
from .models import GlobalSettings
@admin.register(GlobalSettings)
class GSAdmin(admin.ModelAdmin):
    list_display = ('id','free_uses_default','reversed_enabled','reversed_prob','llm_model')
