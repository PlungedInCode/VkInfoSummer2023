from django.contrib import admin
from .models import User, FriendRequest, Friendship

admin.site.register(User)
admin.site.register(FriendRequest)
admin.site.register(Friendship)