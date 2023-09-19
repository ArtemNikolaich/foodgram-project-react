from django.contrib.auth import get_user_model

from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueValidator

from users.models import Follow


UserModel = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Пользовательский сериализатор для создания пользователя.
    """
    username = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=UserModel.objects.all(),
                message='Пользователь с таким именем уже существует.'
            )
        ],
        error_messages={
            'required': 'Имя пользователя обязательно!'
        }
    )

    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=UserModel.objects.all(),
                message='Пользователь с таким адресом'
                        ' электронной почты уже существует.'
            )
        ],
        error_messages={
            'required': 'Email обязателен!'
        }
    )

    class Meta:
        model = UserModel
        fields = tuple(UserModel.REQUIRED_FIELDS) + (
            UserModel.USERNAME_FIELD,
            'password',
        )

    def validate_username(self, value):
        """
        Проверка, что имя пользователя не является "me".
        """
        if value.lower() == 'me':
            raise ValidationError("Имя пользователя 'me' недопустимо!")
        return value


class CustomUserSerializer(UserSerializer):
    """
    Пользовательский сериализатор для пользователя.
    """
    is_subscribed = SerializerMethodField(
        method_name='get_is_subscribed', read_only=True)

    class Meta:
        model = UserModel
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """
        Возвращает информацию о том, подписан ли текущий
        пользователь на пользователя obj.
        """
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and Follow.objects.filter(user=user, author=obj).exists()
        )


class FollowSerializer(CustomUserSerializer):
    """
    Сериализатор для подписки на пользователя.
    """
    recipes_count = SerializerMethodField(method_name='get_recipes_count')
    recipes = SerializerMethodField(method_name='get_recipes')

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes_count', 'recipes')
        read_only_fields = ('email', 'username')

    def validate(self, data):
        """
        Проверяет корректность данных при создании подписки.
        """
        author = self.instance
        user = self.context.get('request').user
        if Follow.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        if user == author:
            raise ValidationError(
                detail='Вы не можете подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST
            )
        return data

    def get_recipes_count(self, obj):
        """
        Возвращает количество рецептов у пользователя obj.
        """
        return obj.recipes.count()

    def get_recipes(self, obj):
        """
        Возвращает список рецептов пользователя obj с ограничением по лимиту.
        """
        from api.serializers import RecipeShortSerializer
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()

        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data
