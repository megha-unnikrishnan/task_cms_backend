from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import CustomUser
from adminview.models import Notification
from .serializers import RegularUserSerializer,UserEditSerializer
import requests
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.permissions import IsAdminUser 
from django.shortcuts import get_object_or_404
from django.contrib import messages

class RegularUserListView(APIView):
    permission_classes = [IsAuthenticated] 
    def get(self, request):
        regular_users = CustomUser.objects.filter(is_staff=False)
        serializer = RegularUserSerializer(regular_users, many=True)     
        return Response(serializer.data)








class EditUserView(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return None

    def get(self, request, pk):
        user = self.get_object(pk)
        if user is None:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserEditSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        user = self.get_object(pk)
        if user is None:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserEditSerializer(user, data=request.data, partial=False)  # Use `partial=True` for partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        user = self.get_object(pk)
        if user is None:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserEditSerializer(user, data=request.data, partial=True)  
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AdminToggleActiveStatusView(APIView):
    def patch(self, request, id):
        user = get_object_or_404(CustomUser, id=id)
        user.is_active = not user.is_active  # Toggle the status
        user.save()
        return Response({"message": f"User is now {'active' if user.is_active else 'inactive'}."})

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        notifications_data = [
            {'id': notification.id, 'message': notification.message, 'created_at': notification.created_at}
            for notification in notifications
        ]
        return Response(notifications_data, status=status.HTTP_200_OK)




from django.shortcuts import render, redirect
from django.contrib import messages


import json


from users.models import Post
from users.serializers import PostSerializer
from rest_framework.exceptions import NotFound



class EditPostUserView(APIView):
    permission_classes = [IsAdminUser]  # Only admin users can access this view

    def get_post_or_404(self, pk):
        """Helper method to fetch a post or raise a 404 error."""
        return get_object_or_404(Post, pk=pk)

    def get(self, request, pk):
        """Retrieve post details."""
        post = self.get_post_or_404(pk)
        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """Update post details."""
        post = self.get_post_or_404(pk)
        serializer = PostSerializer(post, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """Partially update post details."""
        post = self.get_post_or_404(pk)
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





from django.contrib import messages





class PostDeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get_post_or_404(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise NotFound(detail="Post not found.")

    def delete(self, request, pk):
        # Check if the user is an admin or the post author
        post = self.get_post_or_404(pk)
        
        # Allow only admins or the post's author to delete the post
        if not request.user.is_staff and post.author != request.user:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        post.delete()
        return Response({"message": "Post deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
