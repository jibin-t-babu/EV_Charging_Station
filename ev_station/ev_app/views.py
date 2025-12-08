from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.urls import reverse
from django.utils import timezone
import random
from django.http import JsonResponse
from geopy.distance import geodesic
from .forms import VehicleForm
from django.http import HttpResponse
# Create your views here.
@never_cache
def home(request):
    return render(request,"main/home.html")
def about(request):
    return render(request,"main/about.html")
def contact(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']
        myquery=Contact.objects.create(name=name,email=email,message=message)
        myquery.save()
        messages.info(request,"Message sent successfully")
        return redirect('contact')
    return render(request,"main/contact.html")
def services(request):
    return render(request,"main/services.html")
def register_user(request):
    if request.method == "POST":
        firstname = request.POST['fname']
        lastname = request.POST['lname']
        email = request.POST['email']
        username = request.POST['username']
        password=request.POST['password']
        User.objects.create_user(username=username,password=password,first_name=firstname,last_name=lastname,email=email)
        return redirect('login')
    return render(request,"main/register.html")
@never_cache
def login_user(request):
    if request.method == "POST":
        username=request.POST['username']
        password=request.POST['password']
        user=authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            messages.success(request,"Login Successfull")
            return redirect("home")
        else:
            messages.error(request,"Invalid username or password")
            return render(request,"main/login.html")
    else:
      return render(request,"main/login.html")
@never_cache
def stations(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('home')}?alert=please_login")
    station_data = [
        {"id": 1, "name": "GreenCharge Hub", "location": "Calicut", "available_ports": 4, "rating": 4.5},
        {"id": 2, "name": "EcoPlug Station", "location": "Kochi", "available_ports": 2, "rating": 4.2},
        {"id": 3, "name": "ChargeUp EV Point", "location": "Thrissur", "available_ports": 6, "rating": 4.8},
        {"id": 4, "name": "Mall of Mysore", "location": "Mysore", "available_ports": 1, "rating": 3.0},

    ]
    return render(request, "main/stations.html", {"stations": station_data})


@login_required
@never_cache
def book_station(request, station_id):
    station=Station.objects.get(id=station_id)
    if request.method == "POST":
        from datetime import datetime
        booking_date_str = request.POST.get('date')
        time_slot = request.POST.get('time_slot')
        
        booking_date = None
        if booking_date_str:
            try:
                booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
            except ValueError:
                booking_date = None
        
        Booking.objects.create(
            user=request.user,
            station=station,
            date=booking_date,
            time_slot=time_slot,
            status="Confirmed"
        )
        return redirect('my_bookings')
    return render(request,"main/book_station.html",{'station':station})

@never_cache
def my_bookings(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('home')}?alert=please_login")
    status_filter = request.GET.get('status', 'all') 
    bookings = Booking.objects.filter(user=request.user)

    if status_filter != 'all':
        bookings = bookings.filter(status=status_filter)

    context = {
        'bookings': bookings,
        'status_filter': status_filter,
    }
    return render(request, 'main/my_bookings.html', context)


@login_required
@never_cache
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status != "Cancelled":
        booking.status = "Cancelled"
        booking.save()
        messages.info(request, "Booking cancelled successfully.")
    else:
        messages.warning(request, "This booking is already cancelled.")

    return redirect("my_bookings")

@login_required
@never_cache
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'main/booking_detail.html', {'booking': booking})

@login_required(login_url='/login/?alert=please_login')
@never_cache
def station_locator(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('home')}?alert=please_login")
    return render(request, 'main/station_locator.html')

@never_cache
def nearby_stations(request):
    try:
        user_lat = float(request.GET.get('lat', 0))
        user_lon = float(request.GET.get('lon', 0))
    except:
        return JsonResponse({'stations': []})

    stations = Station.objects.all()
    nearby = []

    for station in stations:
        if station.latitude and station.longitude:
            distance = geodesic((user_lat, user_lon), (station.latitude, station.longitude)).km
            if distance <= 20: 
                nearby.append({
                    'id': station.id,
                    'name': station.name,
                    'location': station.location,
                    'latitude': station.latitude,
                    'longitude': station.longitude,
                    'distance': round(distance, 2),
                })

    return JsonResponse({'stations': nearby})

@never_cache
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def charging_progress(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status != "Charging" and booking.status != "Completed":
        booking.status = "Charging"
        booking.charging_progress = 0
        booking.start_time = timezone.now()
        booking.save()
    
    if booking.status == "Charging":
        elapsed_seconds = (timezone.now() - booking.start_time).total_seconds()
        progress = min(100, int((elapsed_seconds / 120) * 100))
        
        booking.charging_progress = progress
        
        if progress >= 100:
            booking.status = "Completed"
            booking.charging_progress = 100
            booking.end_time = timezone.now()
            if not booking.energy_used:
                booking.energy_used = round(random.uniform(12, 35), 2)
            booking.calculate_cost()
            booking.save()
        else:
            booking.save()
    elif booking.status == "Completed":
        progress = 100
    else:
        progress = booking.charging_progress if booking.charging_progress else 0

    context = {
        'booking': booking,
        'progress': progress
    }
    return render(request, 'main/charging_progress.html', context)

@login_required
def charging_summary(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # ✅ DO NOT recalculate if already paid
    if booking.payment_status != "Paid":

        if not booking.energy_used:
            booking.energy_used = round(random.uniform(12, 35), 2)

        if not booking.cost:
            booking.calculate_cost()

        booking.save()

    # ✅ Mark charging completed
    if booking.status == "Charging" and booking.charging_progress >= 100:
        booking.status = "Completed"
        if not booking.end_time:
            booking.end_time = timezone.now()
        booking.save()

    duration = None
    if booking.start_time and booking.end_time:
        duration = booking.end_time - booking.start_time

    return render(request, "main/charging_summary.html", {
        "booking": booking,
        "duration": duration
    })


def payment_page(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # ✅ BLOCK PAYMENT IF CANCELLED
    if booking.status == "Cancelled":
        messages.error(request, "This booking was cancelled. Payment is disabled.")
        return redirect("my_bookings")

    # ✅ BLOCK DOUBLE PAYMENT
    if booking.payment_status == "Paid":
        return redirect("charging_summary", booking_id=booking.id)

    # ✅ Calculate cost only once
    if booking.cost is None:
        if not booking.energy_used:
            booking.energy_used = round(random.uniform(12, 35), 2)
        booking.calculate_cost()
        booking.save()

    if request.method == "POST":
        booking.payment_status = "Paid"
        booking.paid_amount = booking.cost
        booking.save()
        return redirect("charging_summary", booking_id=booking.id)

    return render(request, "main/payment_page.html", {
        "booking": booking,
        "payable_amount": booking.cost
    })



def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.payment_status = "Paid"
    booking.save()

    reward, created = Reward.objects.get_or_create(user=request.user)
    reward.points += 10 
    reward.save()

    return render(request, 'main/payment_success.html', {'booking': booking, 'reward': reward})

@login_required
def my_rewards(request):
    reward, created = Reward.objects.get_or_create(user=request.user)
    return render(request, 'main/rewards.html', {'reward': reward})

@receiver(post_save, sender=Booking)
def notify_admin_new_booking(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            message=f" New booking added by {instance.user.username} at {instance.station.name}"
        )

@receiver(post_save, sender=Station)
def notify_admin_new_station(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            message=f" New station added: {instance.name} - {instance.location}"
        )

@receiver(post_save, sender=Contact)
def notify_admin_new_contact(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            message=f" New contact added: {instance.name} - {instance.email}"
        )

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Vehicle

@login_required
def add_vehicle(request):
    if request.method == "POST":
        name = request.POST.get('name')
        number = request.POST.get('number')
        battery_capacity = request.POST.get('battery_capacity')
        connector_type = request.POST.get('connector_type')

        Vehicle.objects.create(
            user=request.user,
            name=name,
            number=number,
            battery_capacity=battery_capacity,
            connector_type=connector_type
        )

        return redirect('my_vehicles')   # ✅ redirect after saving

    return render(request, 'main/add_vehicles.html')


def my_vehicles(request):
    vehicles=Vehicle.objects.filter(user=request.user)
    return render(request,'main/my_vehicles.html',{'vehicles':vehicles})

@login_required
def delete_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, user=request.user)
    vehicle.delete()
    messages.success(request, "Vehicle deleted.")
    return redirect('my_vehicles')