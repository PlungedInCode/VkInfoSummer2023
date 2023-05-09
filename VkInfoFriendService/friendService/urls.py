"""
URL configuration for friendService project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from friendServiceApp.views import (
    UserRegistrationView, SendFriendRequestView,
    RespondToFriendRequestView,FriendsRequestsView,
    FriendsView, GetFriendshipStatus, RemoveFriendship
)
from .yasg import urlpatterns as doc_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', UserRegistrationView.as_view(), name='user_registration'),
    path('friend-request/', SendFriendRequestView.as_view(), name='send_friend_request'),
    path('friend-request/<int:request_id>/', RespondToFriendRequestView.as_view(), name='respond_to_friend_request'),
    path('user/<int:user_id>/friend-requests/', FriendsRequestsView.as_view(), name='users_friend_requests'),
    path('user/<int:user_id>/friends/', FriendsView.as_view(), name='users_friends'),
    path('user/<int:user_id>/friendship-status/<int:target_user_id>/', GetFriendshipStatus.as_view(), name='friendship_status'),
    path('friendship/<int:friendship_id>/', RemoveFriendship.as_view(), name='remove_friendship'),
]


urlpatterns += doc_urlpatterns