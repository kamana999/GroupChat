from email import message
from rest_framework.permissions import BasePermission
from rest_framework import status
from rest_framework.exceptions import APIException
from .models import BlackListedToken
from django.conf import settings

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if not ( request.user and request.user.is_admin):
            raise GenericApiException('You are not allowed to perform this task')
        return True

class ISUser(BasePermission):
    def has_permission(self, request, view):
        if not ( request.user and request.user.is_user):
            raise GenericApiException('You are not allowed to perform this task')
        return True

class GenericApiException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_code = 'error'

    def __init__(self, detail, status_code =None):
        self.detail = detail
        if status_code is not None:
            self.status_code = status_code
