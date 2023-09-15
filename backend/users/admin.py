from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import Follow, User


class UserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    list_filter = ('is_superuser', 'is_staff', 'is_active')
    search_fields = ('username', 'email')


class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
