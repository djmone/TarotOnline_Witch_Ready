
from django.core.management.base import BaseCommand
from core.models import GlobalSettings
from tarot.models import Deck, Card, SpreadPreset

MAJOR_NAMES = [
    "The Fool","The Magician","The High Priestess","The Empress","The Emperor","The Hierophant",
    "The Lovers","The Chariot","Strength","The Hermit","Wheel of Fortune","Justice",
    "The Hanged Man","Death","Temperance","The Devil","The Tower","The Star","The Moon","The Sun","Judgement","The World"
]
SUITS = [("cups","CUP"), ("swords","SWD"), ("wands","WND"), ("pentacles","PEN")]
RANKS = [("ace","ACE")] + [(f"{i:02d}", f"{i:02d}") for i in range(2,11)] + [("page","PAGE"),("knight","KNIGHT"),("queen","QUEEN"),("king","KING")]

class Command(BaseCommand):
    help = "Create default deck, cards and presets"
    def handle(self, *args, **kwargs):
        gs = GlobalSettings.load()
        d,_ = Deck.objects.get_or_create(slug='rider-waite', defaults={'name':'Rider–Waite'})
        # majors
        for i, nm in enumerate(MAJOR_NAMES):
            code = f"MAJ_{i:02d}"
            Card.objects.get_or_create(deck=d, code=code, defaults={'arcana':'major','suit':'','rank':str(i),'name_ru':nm,'name_en':nm})
        # minors
        for suit, pref in SUITS:
            for rank_name, rank_code in RANKS:
                code = f"{pref}_{rank_code}"
                name = f"{rank_name.title()} of {suit.title()}"
                Card.objects.get_or_create(deck=d, code=code, defaults={'arcana':'minor','suit':suit,'rank':rank_name,'name_ru':name,'name_en':name})
        # presets
        SpreadPreset.objects.get_or_create(slug='celtic-cross', defaults={
            'name':'Кельтский крест','mode':'single','cards_count':10,'price_credits':5,'allow_extra_questions':True,
            'positions_json':[{'index':i+1,'title':f'Позиция {i+1}','description':''} for i in range(10)]
        })
        SpreadPreset.objects.get_or_create(slug='love-relationship', defaults={
            'name':'Отношения','mode':'couple','cards_count':7,'price_credits':4,'allow_extra_questions':True,
            'positions_json':[{'index':i+1,'title':f'Позиция {i+1}','description':''} for i in range(7)]
        })
        SpreadPreset.objects.get_or_create(slug='destiny-path', defaults={
            'name':'Путь/Судьба','mode':'single','cards_count':5,'price_credits':3,'allow_extra_questions':True,
            'positions_json':[{'index':i+1,'title':f'Позиция {i+1}','description':''} for i in range(5)]
        })
        SpreadPreset.objects.get_or_create(slug='choice', defaults={
            'name':'Выбор','mode':'choice','cards_count':3,'price_credits':2,'allow_extra_questions':True,
            'positions_json':[{'index':i+1,'title':f'Вариант {i+1}','description':''} for i in range(3)]
        })
        SpreadPreset.objects.get_or_create(slug='yesno', defaults={
            'name':'Да/Нет','mode':'yesno','cards_count':3,'price_credits':1,'allow_extra_questions':False,
            'positions_json':[{'index':i+1,'title':f'Карта {i+1}','description':''} for i in range(3)]
        })
        self.stdout.write(self.style.SUCCESS("Default deck/cards/presets created"))
