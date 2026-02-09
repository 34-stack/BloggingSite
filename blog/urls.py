from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BlogViewSet, CommentViewSet, UserAuthViewSet

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register("blogs", BlogViewSet, basename="blog")
router.register("auth", UserAuthViewSet, basename="auth")

urlpatterns = [
    path("", include(router.urls)),
    path("blogs/<int:blog_id>/comments/", CommentViewSet.as_view({"get": "list", "post": "create"}), name="blog-comments"),
   
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
