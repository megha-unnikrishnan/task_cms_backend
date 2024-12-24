

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LikePostView,PostDeleteView,PostUpdateView,CustomTokenObtainPairView, RegisterView, AdminOnlyView,LogoutView,PostListView,PostLikeView,PostCreateView,PostDetailView,PostUnlikeView,PostCommentListView,admin_dashboard_view

urlpatterns = [
    path('api/token/', CustomTokenObtainPairView.as_view(), name='get_token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin_dashboard/',admin_dashboard_view,name='admin_dashboard_view'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('admin-only/', AdminOnlyView.as_view(), name='admin_only'),

    path('posts/', PostListView.as_view(), name='post-list'),
    path('posts/create/', PostCreateView.as_view(), name='post-create'),
    path('api/posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:pk>/like/', PostLikeView.as_view(), name='post-like'),
    path('posts/<int:pk>/unlike/', PostUnlikeView.as_view(), name='post-unlike'),
    path('posts/<int:pk>/comments/', PostCommentListView.as_view(), name='post-comments'),
    path('auth/logout/', LogoutView.as_view(), name='logouts'),

    

    path('posts/<int:pk>/update/',PostUpdateView.as_view(),name='updateapi'),
    path('posts/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),

    



     path('posts/<int:pk>/comments/', PostCommentListView.as_view(), name='post-comments'),

       path('posts/<int:post_id>/likes/', LikePostView.as_view(), name='like-post'),

      
]
