from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .permissions import create_groups_and_permissions

@receiver(post_migrate)
def create_groups_and_permissions_on_startup(sender, **kwargs):
    create_groups_and_permissions()