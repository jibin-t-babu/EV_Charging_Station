from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from .models import Booking, Station

@receiver(post_save, sender=Booking)
def notify_admin_new_booking(sender, instance, created, **kwargs):
    if created:
        print(f" New booking added by {instance.user.username} at {instance.station.name}")

@receiver(post_save, sender=Station)
def notify_admin_new_station(sender, instance, created, **kwargs):
    if created:
        print(f" New station added: {instance.name} - {instance.location}")
        
@receiver(post_save, sender=Station)
def notify_admin_new_contact(sender, instance, created, **kwargs):
    if created:
        print(f" New contact added: {instance.name} - {instance.email}")