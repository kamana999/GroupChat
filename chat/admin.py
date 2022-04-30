from django.contrib import admin

from chat.models import Group, User , Message, LikeMessage

# Register your models here.

admin.site.register(User)
admin.site.register(Group)
admin.site.register(Message)
admin.site.register(LikeMessage)