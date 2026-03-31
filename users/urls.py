from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserRegistrationView, UserViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
]
urlpatterns += router.urls