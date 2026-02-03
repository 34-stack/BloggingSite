from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count

from .models import Blog, Comment
from .serializers import BlogListSerializer, BlogDetailSerializer, CommentSerializer
from .permissions import IsAuthorOrReadOnly

# Pagination for comments
class CommentPagination(PageNumberPagination):
    page_size = 5

# Blog APIs
class BlogViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly
    ]

    def get_queryset(self):
        return Blog.objects.select_related("author").annotate(
            likes_count=Count("likes", distinct=True),
            comments_count=Count("comments", distinct=True),
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BlogDetailSerializer
        return BlogListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        blog = self.get_object()
        if request.user in blog.likes.all():
            return Response({"detail": "Already liked"}, status=status.HTTP_400_BAD_REQUEST)
        blog.likes.add(request.user)
        return Response({"detail": "Blog liked"})

    @action(detail=True, methods=["post"])
    def unlike(self, request, pk=None):
        blog = self.get_object()
        if request.user not in blog.likes.all():
            return Response({"detail": "You have not liked this blog"}, status=status.HTTP_400_BAD_REQUEST)
        blog.likes.remove(request.user)
        return Response({"detail": "Blog unliked"})

# Comment APIs
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = CommentPagination

    def get_queryset(self):
        blog_id = self.kwargs["blog_id"]
        return Comment.objects.filter(blog_id=blog_id).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, blog_id=self.kwargs["blog_id"])
