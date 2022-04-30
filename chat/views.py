from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from chat.models import User, Group, Message, LikeMessage
from chat.serializers import UserSerializer, GroupSerializer, MessageSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdmin, ISUser


# Create your views here.


# Normal/Admin User
class UserLogin(APIView):
    def post(self, request):
        user = User.objects.filter(email=request.data.get("email")).first()
        password = request.data.get("password")
        if user is not None and user.check_password(password):
            if user.is_user or user.is_admin:
                refresh = RefreshToken.for_user(user)
                context = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                return Response(context, status.HTTP_200_OK)
            else:
                context = {
                    "message": "Please verify your email first!"
                }
                return Response(context, status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        else:
            context = {
                "detail": "No active account found with the given credentials"
            }
        return Response(context, status.HTTP_401_UNAUTHORIZED)


# Admin User (Get user list allowed by normal user also.)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_user=True)
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['first_name', 'last_name', 'email']

    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch']

    def get_queryset(self):
        return User.objects.filter(is_user=True).exclude(id=self.request.user.id)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsAdmin]
        else:
            self.permission_classes = [IsAuthenticated]
        return super(self.__class__, self).get_permissions()


# Normal User
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    authentication_classes = [JWTAuthentication]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name']
    permission_classes = [IsAuthenticated, ISUser]
    http_method_names = ['get', 'post', 'delete', 'destroy']

    def destroy(self, request, *args, **kwargs):
        group = self.get_object()
        if group.created_by == request.user:
            return super(self.__class__, self).destroy(request, *args, **kwargs)
        else:
            context = {
                "message": "You are not authorized to delete this group!"
            }
            return Response(context, status.HTTP_403_FORBIDDEN)

#Add Member to group
class AddGroupMember(APIView):
    permission_classes = [IsAuthenticated, ISUser]

    def post(self, request, pk):
        group = Group.objects.get(id=pk)
        if group.created_by == request.user:
            user = User.objects.get(id=request.data.get("user_id"))
            if user is not None:
                if user.is_user:
                    if user not in group.members.all():
                        group.members.add(user)
                        context = {
                            "message": "User added successfully!"
                        }
                        return Response(context, status.HTTP_200_OK)
                    else:
                        context = {
                            "message": "User already in group!"
                        }
                        return Response(context, status.HTTP_200_OK)
                else:
                    context = {
                        "message": "User is not a normal user!"
                    }
                    return Response(context, status.HTTP_200_OK)
            else:
                context = {
                    "message": "User does not exist!"
                }
                return Response(context, status.HTTP_200_OK)
        else:
            context = {
                "message": "You are not authorized to add user to this group!"
            }
            return Response(context, status.HTTP_403_FORBIDDEN)


# Message
class MessageView(APIView):
    permission_classes = [IsAuthenticated, ISUser]

    def post(self, request, pk):
        group = Group.objects.get(id=pk)
        if request.user in group.members.all():
            message = Message.objects.create(
                message=request.data.get("message"),
                created_by=request.user,
                group=group
            )
            context = {
                "message_id": message.id,
                "message": message.message,
            }
            return Response(context, status.HTTP_200_OK)
        else:
            context = {
                "detail": "You are not authorized to send message to this group!"
            }
            return Response(context, status.HTTP_403_FORBIDDEN)


class MessageList(ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, ISUser]

    def get_queryset(self):
        group = Group.objects.get(id=self.kwargs.get("pk"))
        if self.request.user in group.members.all():
            return Message.objects.filter(group=group)
        else:
            return None


class LikeUnlikeMessageView(APIView):
    permission_classes = [IsAuthenticated, ISUser]

    def post(self, request, pk):
        message = Message.objects.get(id=pk)
        like = LikeMessage.objects.filter(message=message, created_by=request.user).first()
        if not like:
            like = LikeMessage.objects.create(
                message=message,
                created_by=request.user
            )
            like.save()
            context = {
                "message": "Message liked successfully!"
            }
            return Response(context, status.HTTP_200_OK)
        else:
            like.delete()
            context = {
                "message": "Message Unliked successfully!"
            }
            return Response(context, status.HTTP_200_OK)