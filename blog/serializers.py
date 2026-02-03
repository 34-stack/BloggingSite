from rest_framework import serializers
from .models import Blog, Comment

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ["id", "author", "content", "created_at"]

class BlogListSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Blog
        fields = ["id", "title", "author", "likes_count", "comments_count", "created_at"]

class BlogDetailSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)
    latest_comments = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = ["id", "title", "content", "author", "likes_count", "comments_count", "latest_comments", "created_at"]

    def get_latest_comments(self, obj):
        comments = obj.comments.order_by("-created_at")[:5]
        return CommentSerializer(comments, many=True).data
