from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ApplicationHistory
from .notifications import send_status_notification


@receiver(post_save, sender=ApplicationHistory)
def notify_on_status_change(sender, instance, created, **kwargs):
    if created and instance.to_status:
        send_status_notification(
            application=instance.application,
            to_status=instance.to_status,
            remarks=instance.remarks or '',
        )
