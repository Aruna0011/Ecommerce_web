from django.urls import path
from truckbrand import views

urlpatterns = [
    path('', views.index, name="index"),
    path('about/', views.about, name="about"),
    path('contact', views.contact, name="contact"),
    path('profile/', views.profile, name="profile"),
    path('checkout/', views.checkout, name='checkout'),
    path('order_summary/', views.show_order_summary, name='order_summary'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
]