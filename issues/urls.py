from django.urls import path
from .views import IssueListCreateView, IssueDetailView, CommentListCreateView, CommentDetailView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = router.urls + [
    path('issues/', IssueListCreateView.as_view(), name='issue-list-create'),
    path('issues/<int:pk>/', IssueDetailView.as_view(), name='issue-detail'),
    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
]