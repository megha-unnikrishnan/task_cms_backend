from django.urls import path
from .views import PostDeleteUserView,EditPostUserView,deletepost,update_posts_users,edit_user,fetch_posts_users_admin,AdminToggleActiveStatusView,admin_toggle_active_status_view,RegularUserListView,EditUserView,regular_users_view

urlpatterns = [
    path('regular-users/', RegularUserListView.as_view(), name='regular-users'),
    path('regular-users-list/', regular_users_view, name='regular_users_view'),
    path('edit-user/<int:pk>/', EditUserView.as_view(), name='edit_user'),
    path('edit_user/<int:id>/',edit_user,name='edit_user'),
    path('toggle-active-status/<int:id>/', AdminToggleActiveStatusView.as_view(), name='toggle_active_status'),
    path('block-unblock/<int:user_id>/', admin_toggle_active_status_view, name='block_unblock'),
    path('fetch_posts_users_admin/',fetch_posts_users_admin,name='fetch_posts_users_admin'),
    path('posts-users/<int:pk>/update/',EditPostUserView.as_view(),name='updateapiadmin'),
    path('update_posts_users/<int:pk>/', update_posts_users, name='update_posts_users'),
    path('deleteuser/<int:pk>/',PostDeleteUserView.as_view(),name='delete_user_posts'),
    path('delete_posts_users/<int:pk>/', deletepost, name='delete'),
]
