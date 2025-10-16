from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'listings', views.ListingViewSet, basename='listing')
router.register(r'bookings', views.BookingViewSet, basename='booking')

urlpatterns = router.urls + [
    path('payment/process/', views.process_payment, name='process_payment'),
    path('payment/verify/', views.verify_payment, name='verify_payment'),
]