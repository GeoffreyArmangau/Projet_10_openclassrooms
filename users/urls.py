from django.urls import path
from .views import UserRegistrationView
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = router.urls + [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
]