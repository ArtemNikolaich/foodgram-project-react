from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from recipes.models import Recipe
from users.models import Follow, User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name',
                    'num_following', 'num_followers', 'num_recipes')
    list_filter = ('is_superuser', 'is_staff', 'is_active')
    search_fields = ('username', 'email')

    def num_following(self, obj):
        return Follow.objects.filter(user=obj).count()
    num_following.short_description = 'Количество подписок'

    def num_followers(self, obj):
        return Follow.objects.filter(author=obj).count()
    num_followers.short_description = 'Количество подписчиков'

    def num_recipes(self, obj):
        return Recipe.objects.filter(author=obj).count()
    num_recipes.short_description = 'Количество рецептов'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
