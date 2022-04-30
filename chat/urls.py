from django.urls import path, include
from .views import UserViewSet, UserLogin, GroupViewSet, AddGroupMember, MessageView, MessageList,\
     LikeUnlikeMessageView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'group', GroupViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token', UserLogin.as_view(), name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('group_member/<int:pk>/add', AddGroupMember.as_view(), name='add_member'),
    path('group_message/<int:pk>/add', MessageView.as_view(), name='add_message'),
    path('group_message/<int:pk>/list', MessageList.as_view(), name='list_message'),
    path('message/<int:pk>/like_unlike', LikeUnlikeMessageView.as_view(), name='like_unlike_message'),
    ]
