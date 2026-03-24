from django.urls import path
from .views import UserRegistrationView, ProjectListCreateView, ProjectDetailView, IssueListCreateView, IssueDetailView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('projects/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('issues/', IssueListCreateView.as_view(), name='issue-list-create'),
    path('issues/<int:pk>/', IssueDetailView.as_view(), name='issue-detail'),
]
