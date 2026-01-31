from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import BlogViewSet, RegisterView, LikeToggleAPIView, CommentViewSet

router = DefaultRouter()
router.register('blogs', BlogViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),

    path('blogs/<int:blog_id>/like/', LikeToggleAPIView.as_view(), name='like-blog'),

    path('blogs/<int:blog_id>/comments/',
         CommentViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='comments'),

    path('', include(router.urls)),
]
