from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, ContributorViewSet

router = DefaultRouter()
router.register(r'', ProjectViewSet, basename='project')

contributor_list = ContributorViewSet.as_view({'get': 'list', 'post': 'create'})
contributor_detail = ContributorViewSet.as_view({'delete': 'destroy'})

urlpatterns = router.urls + [
    path('<int:project_pk>/contributors/', contributor_list, name='contributor-list'),
    path('<int:project_pk>/contributors/<int:pk>/', contributor_detail, name='contributor-detail'),
]
