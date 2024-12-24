


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, UserSerializer
from rest_framework.permissions import AllowAny
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import RegisterSerializer,PostSerializer,CommentSerializer,LikeSerializer
from .models import CustomUser,Comment,Like,Post
from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import PermissionDenied
from .models import CustomUser
from django.contrib.auth.decorators import login_required

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        # Log detailed errors
        print("Validation errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        




import requests
from django.shortcuts import render, redirect

    








def admin_dashboard_view(request):
    return render(request, 'admin/admin_dashboard.html')

class AdminOnlyView(APIView):
    def get(self, request):
        if not request.user.is_staff:
            return Response({"error": "Only admins are allowed."}, status=status.HTTP_403_FORBIDDEN)
        return Response({"message": "Welcome, Admin!"})


# Create a Post


class PostCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print(f"Logged-in user: {request.user}")

        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(f"Validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostListView(APIView):
    permission_classes = [IsAuthenticated]
    

    def get(self, request):
        if not request.user.is_active:
            return Response({"error": "Your account is inactive. Please contact support."}, status=status.HTTP_403_FORBIDDEN)
        posts = Post.objects.all() 
        serializer = PostSerializer(posts, many=True)  
        return Response(serializer.data) 


from django.http import HttpResponseServerError  
import requests
from django.shortcuts import render, redirect
from django.contrib import messages 




from django.shortcuts import render, redirect
import requests

class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            serializer = PostSerializer(post)
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response({"detail": "Post not found"}, status=404)


from django.shortcuts import get_object_or_404


class PostUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk, *args, **kwargs):
        try:
            post = Post.objects.get(pk=pk, author=request.user)
        except Post.DoesNotExist:
            return Response({"error": "Post not found or you do not have permission to edit this post."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PostDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, *args, **kwargs):
        try:
            post = Post.objects.get(pk=pk, author=request.user)
            post.delete()
            return Response({"message": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response({"error": "Post not found or you do not have permission to delete this post."}, status=status.HTTP_404_NOT_FOUND)







# Like a Post
class PostLikeView(generics.CreateAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def create(self, request, *args, **kwargs):
        post_id = self.kwargs.get('pk')
        post = Post.objects.get(id=post_id)
        user = request.user
        
       
        if Like.objects.filter(post=post, user=user).exists():
            return Response({"detail": "You have already liked this post"}, status=status.HTTP_400_BAD_REQUEST)
        
     
        like = Like.objects.create(post=post, user=user)
        post.likes_count += 1
        post.save()
        return Response(self.get_serializer(like).data, status=status.HTTP_201_CREATED)


class PostUnlikeView(generics.DestroyAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def perform_destroy(self, instance):
        instance.post.likes_count -= 1
        instance.post.save()
        super().perform_destroy(instance)

# Get Comments for a Post

class PostCommentListView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('pk')
        return Comment.objects.filter(post_id=post_id)

    def perform_create(self, serializer):
        post_id = self.kwargs.get('pk')
        post = Post.objects.get(id=post_id)
        serializer.save(post=post, author=self.request.user)



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            
            refresh_token = request.headers.get('Authorization').split(' ')[1]  # Extract token from 'Bearer <token>'

            if not refresh_token:
                return Response({"detail": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

            
            token = RefreshToken(refresh_token)

            
            token.blacklist()

            return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)

        except TokenError:
            return Response({"detail": "Invalid token or already blacklisted"}, status=status.HTTP_400_BAD_REQUEST)
        





from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import requests








class LikePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        user = request.user
        post = Post.objects.get(id=post_id)
        like, created = Like.objects.get_or_create(post=post, user=user)
        if not created:  # If the like already exists, delete it (unlike)
            like.delete()
            return Response({"message": "Unliked", "liked": False, "likes_count": post.likes.count()})
        
        return Response({"message": "Liked", "liked": True, "likes_count": post.likes.count()})
    def get(self, request, post_id):
        user = request.user
        post = Post.objects.get(id=post_id)
        liked = Like.objects.filter(post=post, user=user).exists()  # Check if the user has liked the post
        likes_count = post.likes.count()  # Get the total number of likes

        return Response({"liked": liked, "likes_count": likes_count})

