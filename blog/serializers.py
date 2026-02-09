from rest_framework import serializers
from .models import Blog, Comment
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

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

# User Serializers
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']

    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({"password": "Passwords do not match"})
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Username already exists"})
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Email already exists"})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        data['user'] = user
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
