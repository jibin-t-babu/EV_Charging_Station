from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.
class Station(models.Model):
    name=models.CharField(max_length=100)
    location=models.CharField(max_length=100)
    available_ports=models.IntegerField(default=0)
    rating=models.FloatField(default=0.0)
    latitude = models.FloatField()
    longitude = models.FloatField()
    def __str__(self):
        return self.name
    
class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Charging', 'Charging'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    station=models.ForeignKey(Station, on_delete=models.CASCADE)
    date=models.DateField(null=True, blank=True)
    time_slot=models.CharField(max_length=50, null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    energy_used = models.FloatField(null=True, blank=True)
    cost = models.FloatField(null=True, blank=True)
    charging_progress = models.IntegerField(default=0)
    status=models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    amount=models.DecimalField(max_digits=10, decimal_places=2, default=100)
    payment_status=models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending')
    paid_amount = models.FloatField(null=True, blank=True)
    vehicle = models.ForeignKey('Vehicle', on_delete=models.SET_NULL, null=True, blank=True)
    def calculate_cost(self):
        rate_per_kwh = 12
        if self.energy_used:
            self.cost = self.energy_used * rate_per_kwh
            self.save()
        return self.cost

    def __str__(self):
        return f"{self.user.username} - {self.station.name} - {self.date if self.date else self.created_at}"

class Reward(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.points} pts"

@receiver(post_save, sender=User)
def create_user_reward(sender, instance, created, **kwargs):
    if created:
        Reward.objects.create(user=instance)

class Contact(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField(max_length=100)
    message=models.TextField(max_length=1000)
    def __str__(self):
        return self.name

class Notification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.message[:50]}..."

class Vehicle(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    number=models.CharField(max_length=20,unique=True)
    name=models.CharField(max_length=100)
    battery_capacity=models.IntegerField()
    connector_type=models.CharField(max_length=50)
    def __str__(self):
        return f"{self.number}-{self.name}"
