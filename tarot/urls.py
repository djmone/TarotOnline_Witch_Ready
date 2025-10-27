
from django.urls import path
from . import views
app_name='tarot'
urlpatterns = [
  path('', views.home, name='home'),
  path('start/', views.start_form, name='start_form'),
  path('start/<slug:preset_slug>/', views.start_session, name='start'),
  path('deal/<int:session_id>/', views.deal_api, name='deal'),
  path('interpret/full/<int:session_id>/', views.interpret_full, name='interpret_full'),
  path('interpret/step/<int:session_id>/', views.interpret_step, name='interpret_step'),
  path('pdf/<int:session_id>/', views.export_pdf, name='pdf'),
]
