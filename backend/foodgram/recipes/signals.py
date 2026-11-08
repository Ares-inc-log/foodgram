from django.db.models.signals import post_save
from django.dispatch import receiver

from blog.models import Recipe, ShortLink


@receiver(post_save, sender=Recipe)
def create_recipe_short_link(sender, instance, created, **kwargs):
    if created:
        ShortLink.objects.create(recipe=instance)
