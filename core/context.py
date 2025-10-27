from .models import GlobalSettings

def global_settings_context(request):
    return {'gs': GlobalSettings.load()}
