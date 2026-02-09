from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Count

from .models import Blog, Comment
from .serializers import BlogListSerializer, BlogDetailSerializer, CommentSerializer, UserRegistrationSerializer, UserLoginSerializer, UserSerializer
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

    @action(detail=False, methods=["post"])
    def like(self, request, pk=None):
        blog_id = request.data.get('id')
        blog = Blog.objects.get(id=blog_id)
        if request.user in blog.likes.all():
            return Response({"detail": "Already liked"}, status=status.HTTP_400_BAD_REQUEST)
        blog.likes.add(request.user)
        return Response({"detail": "Blog liked"})

    @action(detail=False, methods=["post"])
    def unlike(self, request, pk=None):
        blog_id=request.data.get('id')
        blog=Blog.objects.get(id=blog_id)
        if request.user not in blog.likes.all():
            return Response({"detail": "You have not liked this blog"}, status=status.HTTP_400_BAD_REQUEST)
        blog.likes.remove(request.user)
        return Response({"detail": "Blog unliked"})

# Comment APIs
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = CommentPagination
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        blog_id = self.kwargs["blog_id"]
        return Comment.objects.filter(blog_id=blog_id).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

# User Authentication APIs
class UserAuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "detail": "User registered successfully"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "detail": "Login successful"
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def logout(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
