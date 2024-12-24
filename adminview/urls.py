from django.urls import path
from .views import NotificationListView,PostDeleteUserView,EditPostUserView,AdminToggleActiveStatusView,RegularUserListView,EditUserView

urlpatterns = [
    path('regular-users/', RegularUserListView.as_view(), name='regular-users'),
    path('edit-user/<int:pk>/', EditUserView.as_view(), name='edit_user'),
    path('toggle-active-status/<int:id>/', AdminToggleActiveStatusView.as_view(), name='toggle_active_status'),
    path('posts-users/<int:pk>/update/',EditPostUserView.as_view(),name='updateapiadmin'),
    path('deleteuser/<int:pk>/',PostDeleteUserView.as_view(),name='delete_user_posts'),
    path('api/notifications/', NotificationListView.as_view(), name='get_notifications'),
]
