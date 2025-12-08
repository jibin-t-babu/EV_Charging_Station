from django.urls import path
from ev_app import views

urlpatterns=[
    path('', views.home,name="home"),
    path('about/',views.about,name="about"),
    path('services/',views.services,name="services"),
    path('contact/',views.contact,name="contact"),
    path('login/',views.login_user,name="login"),
    path('register/',views.register_user,name="register"),
    path('stations/',views.stations,name="stations"),
    path('book/<int:station_id>/',views.book_station,name="book_station"),
    path('my-bookings/',views.my_bookings,name="my_bookings"),
    path('cancel-booking/<int:booking_id>/',views.cancel_booking,name='cancel_booking'),
    path('booking/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('station-locator/', views.station_locator, name='station_locator'),
    path('nearby-stations/', views.nearby_stations, name='nearby_stations'),
    path('logout/',views.logout_view,name="logout"),
    path('charging/<int:booking_id>/', views.charging_progress, name='charging_progress'),
    path('charging-summary/<int:booking_id>/', views.charging_summary, name='charging_summary'),
    path('payment/<int:booking_id>/', views.payment_page, name='payment_page'),
    path('payment-success/<int:booking_id>/', views.payment_success, name='payment_success'),
    path('my-rewards/', views.my_rewards, name='my_rewards'),
    path('add-vehicle/',views.add_vehicle, name='add_vehicle'),
    path('my-vehicles/',views.my_vehicles, name='my_vehicles'),
    path('vehicle/delete/<int:pk>/',views.delete_vehicle,name="delete_vehicle")

]