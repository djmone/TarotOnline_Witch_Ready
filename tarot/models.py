
from django.db import models
from django.utils.translation import gettext_lazy as _

class Deck(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    back_image = models.ImageField(upload_to='cards/images/', blank=True, null=True)
    theme_class = models.CharField(max_length=50, default='theme-witch')
    def __str__(self): return self.name

class Card(models.Model):
    class Arcana(models.TextChoices):
        MAJOR = 'major', _('Major')
        MINOR = 'minor', _('Minor')
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    code = models.CharField(max_length=40)
    arcana = models.CharField(max_length=10, choices=Arcana.choices)
    suit = models.CharField(max_length=20, blank=True)
    rank = models.CharField(max_length=10, blank=True)
    name_ru = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    img_upright = models.ImageField(upload_to='cards/images/', null=True, blank=True)
    img_reversed = models.ImageField(upload_to='cards/images/', null=True, blank=True)
    class Meta:
        unique_together = ('deck','code')
    def __str__(self): return f"{self.deck.slug}:{self.code}"

class SpreadPreset(models.Model):
    class Mode(models.TextChoices):
        SINGLE = 'single', _('Single person')
        COUPLE = 'couple', _('Two persons')
        CHOICE  = 'choice', _('Choice (3)')
        YESNO   = 'yesno', _('Yes/No')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    mode = models.CharField(max_length=10, choices=Mode.choices)
    cards_count = models.IntegerField()
    price_credits = models.IntegerField(default=0)
    allow_extra_questions = models.BooleanField(default=False)
    positions_json = models.JSONField(default=list)
    def __str__(self): return self.name

class SpreadSession(models.Model):
    class Reveal(models.TextChoices):
        STEP = 'step', _('Per-card')
        ALL  = 'all',  _('All at once')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    preset = models.ForeignKey(SpreadPreset, on_delete=models.PROTECT)
    deck = models.ForeignKey(Deck, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    seed = models.CharField(max_length=64)
    seed_hash = models.CharField(max_length=64)
    reversed_enabled = models.BooleanField(default=True)
    reversed_prob = models.FloatField(default=0.5)
    reveal_mode = models.CharField(max_length=10, choices=Reveal.choices, default=Reveal.ALL)
    p1_name = models.CharField(max_length=80)
    p1_dob  = models.DateField(null=True, blank=True)
    p2_name = models.CharField(max_length=80, blank=True)
    p2_dob  = models.DateField(null=True, blank=True)
    extra_questions = models.TextField(blank=True)
    cards_json = models.JSONField(default=list)
    committed = models.BooleanField(default=False)

class SpreadReading(models.Model):
    session = models.OneToOneField(SpreadSession, on_delete=models.CASCADE, related_name='reading')
    model = models.CharField(max_length=100)
    prompt_used = models.TextField()
    temperature = models.FloatField(default=0.6)
    tokens = models.IntegerField(default=0)
    response_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
