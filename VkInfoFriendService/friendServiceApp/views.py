from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from .models import User, FriendRequest, Friendship
from .serializers import UserSerializer, FriendRequestSerializer, FriendshipSerializer


class UserRegistrationView(generics.CreateAPIView):
    """Зарегистрировать нового пользователя"""
    serializer_class = UserSerializer
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendFriendRequestView(generics.CreateAPIView): 
    """Отправить одному пользователю заявку в друзья другому"""
    serializer_class = FriendRequestSerializer
    def post(self, request):
        serializer = FriendRequestSerializer(data=request.data)
        if serializer.is_valid():
            sender = serializer.validated_data['sender']    
            recipient = serializer.validated_data['recipient']
            req_status = serializer.validated_data['status']
            if req_status != "pending":
                return Response({"Ошибка":"Статус должен быть \"pending\" "}, status=status.HTTP_400_BAD_REQUEST)
            if sender == recipient:
                return Response({"Ошибка":"Пользователь не может отправить запрос самому"}, status=status.HTTP_400_BAD_REQUEST)
            elif Friendship.objects.filter(user1=sender, user2=recipient).exists() or Friendship.objects.filter(user1=recipient, user2=sender).exists():
                return Response({"Ошибка":"Пользователи уже являются друзьями"}, status=status.HTTP_400_BAD_REQUEST)
            elif FriendRequest.objects.filter(sender=sender, recipient=recipient).exists():
                return Response({"Ошибка":"Запрос уже отправлен"}, status=status.HTTP_400_BAD_REQUEST)
            elif FriendRequest.objects.filter(sender=recipient, recipient=sender).exists():
                Friendship.objects.create(user1=sender, user2=recipient)
                new_request = serializer.save(status="accepted")
                old_request = FriendRequest.objects.filter(sender=recipient, recipient=sender)
                old_request.delete()
                return Response(FriendRequestSerializer(new_request).data, status=status.HTTP_201_CREATED)
            else:
                friend_request = serializer.save(sender=sender)
                return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RespondToFriendRequestView(APIView):
    """Принять/отклонить пользователю заявку в друзья от другого пользователя"""
    def put(self, request, request_id):
        try:
            friend_request = FriendRequest.objects.get(id=request_id)
        except FriendRequest.DoesNotExist:
            return Response({"Ошибка":"Запрос не найден"}, status=status.HTTP_404_NOT_FOUND)

        serializer = FriendRequestSerializer(friend_request, data=request.data, partial=True)
        if serializer.is_valid():
            friend_request = serializer.save()
            if friend_request.status == 'accepted':
                Friendship.objects.create(user1=friend_request.sender, user2=friend_request.recipient)
            return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FriendsRequestsView(APIView):
    """Посмотреть пользователю список своих исходящих и входящих заявок в друзья"""
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:   
            return Response({"Ошибка":"Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
            
        incoming_requests = FriendRequest.objects.filter(recipient=user_id)
        outgoing_requests = FriendRequest.objects.filter(sender=user_id)
        incoming_serializer = FriendRequestSerializer(incoming_requests, many=True)
        outgoing_serializer = FriendRequestSerializer(outgoing_requests, many=True)
        return Response({
                "Входящие заявки":incoming_serializer.data,
                "Исходящие заявки":outgoing_serializer.data
            }, status=status.HTTP_200_OK)
        

class FriendsView(APIView):
    """Посмотреть пользователю список своих друзей"""
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"Ошибка":"Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

        friendships = Friendship.objects.filter(user1=user) | Friendship.objects.filter(user2=user)
        friends = []
        for friendship in friendships:
            if friendship.user1 == user:
                friends.append(friendship.user2)
            else:
                friends.append(friendship.user1)

        serializer = UserSerializer(friends, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetFriendshipStatus(APIView):
    """Получить пользователю статус дружбы с каким-то другим пользователем 
    (нет ничего / есть исходящая заявка / есть входящая заявка / уже друзья)"""
    def get(self, request, user_id, target_user_id):
        try:
            user = User.objects.get(id=user_id)
            target_user = User.objects.get(id=target_user_id)
        except User.DoesNotExist:
            return Response({"Ошибка":"Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
        
        friendship = Friendship.objects.filter(user1=user, user2=target_user).exists() or Friendship.objects.filter(user1=target_user, user2=user).exists()
        
        if friendship:
            return Response({"Статус":"уже друзья"}, status=status.HTTP_200_OK)
        elif FriendRequest.objects.filter(sender=user, recipient=target_user).exists():
            return Response({"Статус":"есть исходящая заявка"}, status=status.HTTP_200_OK)
        elif FriendRequest.objects.filter(sender=target_user, recipient=user).exists():
            return Response({"Статус":"есть входящая заявка"}, status=status.HTTP_200_OK)

        return Response({"Статус":"нет ничего"}, status=status.HTTP_200_OK)
    

class RemoveFriendship(APIView):
    """Удалить пользователю другого пользователя из своих друзей"""
    def delete(self, request, friendship_id):
        try:
            friendship = Friendship.objects.get(id=friendship_id)
        except Friendship.DoesNotExist:
            return Response({"Ошибка": "Дружба не существует"}, status=status.HTTP_404_NOT_FOUND)
        friendship.delete()

        FriendRequest.objects.filter(sender=friendship.user1, recipient=friendship.user2).delete()
        FriendRequest.objects.filter(sender=friendship.user2, recipient=friendship.user1).delete()


        return Response({"Статус": "Дружба удалена успешно"}, status=status.HTTP_200_OK)