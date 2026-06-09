from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DestinationViewSet, HotelViewSet, HotelBookingViewSet, DestinationReviewViewSet
)

router = DefaultRouter()
router.register(r'destinations', DestinationViewSet)
router.register(r'hotels', HotelViewSet)
router.register(r'hotel-bookings', HotelBookingViewSet)
router.register(r'destination-reviews', DestinationReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
]