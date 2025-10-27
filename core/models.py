
from django.db import models

class GlobalSettings(models.Model):
    singleton = models.BooleanField(default=True, editable=False)
    free_uses_default = models.IntegerField(default=2)
    reversed_enabled = models.BooleanField(default=True)
    reversed_prob = models.FloatField(default=0.5)
    disclaimer_ru = models.TextField(blank=True, default='Только для развлечения.')
    disclaimer_en = models.TextField(blank=True, default='For entertainment purposes only.')
    ollama_base_url = models.CharField(max_length=200, default='http://localhost:11434')
    llm_model = models.CharField(max_length=100, default='qwen2.5:14b')
    llm_temperature = models.FloatField(default=0.6)
    llm_max_tokens = models.IntegerField(default=1200)

    def save(self,*a,**kw):
        self.pk = 1
        super().save(*a,**kw)

    @classmethod
    def load(cls):
        obj,_ = cls.objects.get_or_create(pk=1)
        return obj
