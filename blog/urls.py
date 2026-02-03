from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BlogViewSet, CommentViewSet

router = DefaultRouter()
router.register("blogs", BlogViewSet, basename="blog")

urlpatterns = [
    path("", include(router.urls)),
    path("blogs/<int:blog_id>/comments/", CommentViewSet.as_view({"get": "list", "post": "create"}), name="blog-comments"),
]
