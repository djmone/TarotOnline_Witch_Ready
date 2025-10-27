
from django.contrib import admin
from .models import Deck, Card, SpreadPreset, SpreadSession, SpreadReading
@admin.register(Deck) 
class DeckAdmin(admin.ModelAdmin): list_display=('id','name','slug')
@admin.register(Card) 
class CardAdmin(admin.ModelAdmin): list_display=('deck','code','arcana','suit','rank','name_ru')
@admin.register(SpreadPreset) 
class PresetAdmin(admin.ModelAdmin): list_display=('name','slug','mode','cards_count','price_credits','allow_extra_questions')
@admin.register(SpreadSession) 
class SessionAdmin(admin.ModelAdmin): list_display=('id','user','preset','created_at','reveal_mode','committed')
@admin.register(SpreadReading) 
class ReadingAdmin(admin.ModelAdmin): list_display=('session','model','created_at')
