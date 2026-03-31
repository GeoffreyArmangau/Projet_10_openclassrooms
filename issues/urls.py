from rest_framework.routers import DefaultRouter
from .views import IssueViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'issues', IssueViewSet, basename='issue')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = router.urls