from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, ContributorViewSet
from issues.views import IssueViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'', ProjectViewSet, basename='project')

contributor_list = ContributorViewSet.as_view({'get': 'list', 'post': 'create'})
contributor_detail = ContributorViewSet.as_view({'delete': 'destroy'})

issue_list = IssueViewSet.as_view({'get': 'list', 'post': 'create'})
issue_detail = IssueViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})

comment_list = CommentViewSet.as_view({'get': 'list', 'post': 'create'})
comment_detail = CommentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})

urlpatterns = router.urls + [
    path('<int:project_pk>/contributors/', contributor_list, name='contributor-list'),
    path('<int:project_pk>/contributors/<int:pk>/', contributor_detail, name='contributor-detail'),
    path('<int:project_pk>/issues/', issue_list, name='issue-list'),
    path('<int:project_pk>/issues/<int:pk>/', issue_detail, name='issue-detail'),
    path('<int:project_pk>/issues/<int:issue_pk>/comments/', comment_list, name='comment-list'),
    path('<int:project_pk>/issues/<int:issue_pk>/comments/<int:pk>/', comment_detail, name='comment-detail'),
]
