import re
from tokenize import group
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.state import token_backend

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name','last_name',  'email', 'password','is_user', 'is_admin')
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = User(
            is_admin=validated_data['is_admin'],
            is_user=validated_data['is_user'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.is_admin = validated_data.get('is_admin', instance.is_admin)
        instance.is_user = validated_data.get('is_user', instance.is_user)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.set_password(validated_data.get('password', instance.password))
        instance.save()
        return instance
    
    def validate(self,data):
        if data.get('is_admin',None)==None:
            data['is_admin']=False
        return data


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'description', 'created_by', 'created_at')
        extra_kwargs = {'created_by': {'required': False}}

    def create(self, validated_data):
        user =  self.context['request'].user
        group = Group(
            name=validated_data['name'],
            description=validated_data['description'],
            created_by=user
        )
        group.save()
        group.members.add(user.id)
        return group


class MinUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name')


class LikeByUserSerializer(serializers.ModelSerializer):
    liked_by = MinUserSerializer(read_only=True)
    class Meta:
        model = LikeMessage
        fields = ('id', 'liked_by', 'created_at')
        extra_kwargs = {'created_by': {'required': False}}


class MessageSerializer(serializers.ModelSerializer):
    message_by = MinUserSerializer(read_only=True)
    likes = serializers.IntegerField(read_only=True)
    liked_by_user = LikeByUserSerializer(read_only=True, many=True)
    class Meta:
        model = Message
        fields = ('id', 'message', 'message_by', 'likes', 'liked_by_user', 'group', 'created_at')
        extra_kwargs = {'created_by': {'required': False}}

    def create(self, validated_data):
        user =  self.context['request'].user
        message = Message(
            message=validated_data['message'],
            created_by=user,
            group=validated_data['group']
        )
        message.save()
        return message


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super(CustomTokenRefreshSerializer, self).validate(attrs)
        return data
