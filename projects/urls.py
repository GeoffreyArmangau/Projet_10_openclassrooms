from django.urls import path
from .views import ProjectListCreateView, ProjectDetailView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = router.urls + [
    path('projects/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
]
