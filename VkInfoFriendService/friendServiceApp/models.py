from django.db import models

class User(models.Model):
    """Пользовтели"""
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.username


class FriendRequest(models.Model):
    """Заявки в друзья"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')
    )

    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_requests_sent')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_requests_received')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Friend request from {self.sender.username} to {self.recipient.username}"


class Friendship(models.Model):
    """Дружба"""
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friends2')

    def __str__(self):
        return f"Friendship between {self.user1.username} and {self.user2.username}"
