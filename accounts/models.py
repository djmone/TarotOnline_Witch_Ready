
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    free_uses_remaining = models.IntegerField(default=2)
    credits = models.IntegerField(default=0)
    def __str__(self): return f"Profile({self.user.username})"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
