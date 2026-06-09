from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ProfileViewSet, 
    LoginView, LogoutView, DashboardStatsView
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
#router.register(r'roles', RoleViewSet)
router.register(r'profiles', ProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', UserViewSet.as_view({'post': 'create'}), name='register'),
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard'),
]