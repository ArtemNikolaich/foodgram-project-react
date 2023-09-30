from django.db.models import F
from django.shortcuts import get_object_or_404

from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from foodgram.constants import INGREDIENT_MIN_AMOUNT, COOKING_TIME_MIN_VALUE
from recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from users.serializers import CustomUserSerializer


class IngredientSerializer(ModelSerializer):
    """
    Сериализатор для ингредиентов.
    """
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(ModelSerializer):
    """
    Сериализатор для тегов.
    """
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeReadSerializer(ModelSerializer):
    """
    Сериализатор для чтения рецепта.
    """
    tags = TagSerializer(many=True, read_only=True)
    ingredients = SerializerMethodField(method_name='get_ingredients')
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = SerializerMethodField(
        method_name='get_is_favorited', read_only=True)
    is_in_shopping_cart = SerializerMethodField(
        method_name='get_is_in_shopping_cart', read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'text',
            'image',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        """
        Возвращает список ингредиентов рецепта.
        """
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredientinrecipe__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        """
        Проверяет, добавлен ли рецепт в избранное текущим пользователем.
        """
        user = self.context.get('request').user

        return (
            user.is_authenticated
            and user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """
        Проверяет, добавлен ли рецепт в корзину покупок текущим пользователем.
        """
        user = self.context.get('request').user

        return (
            user.is_authenticated
            and user.shopping_cart.filter(recipe=obj).exists()
        )


class IngredientInRecipeWriteSerializer(ModelSerializer):
    """
    Сериализатор для записи ингредиентов в рецепт.
    """
    id = IntegerField(write_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeWriteSerializer(ModelSerializer):
    """
    Сериализатор для создания и обновления рецепта.
    """
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeWriteSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, value):
        """
        Проверяет валидность списка ингредиентов.
        """
        ingredients = value

        if not ingredients:
            raise ValidationError(
                'Совсем без ингредиента нельзя!'
            )

        ingredients_list = []

        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=item['id'])
            if ingredient in ingredients_list:
                raise ValidationError(
                    'Ингредиенты не должны повторяться!'
                )
            if int(item['amount']) < INGREDIENT_MIN_AMOUNT:
                raise ValidationError(
                    'Ингредиента должно быть хоть сколько-то!'
                )
            ingredients_list.append(ingredient)
        return value

    def validate_tags(self, value):
        """
        Проверяет валидность списка тегов.
        """
        tags = value

        if not tags:
            raise ValidationError(
                'Совсем без тегов нельзя!'
            )

        if len(tags) != len(set(tags)):
            raise ValidationError(
                'Теги должны быть уникальными!'
            )

        return value

    def validate_cooking_time(self, value):
        """
        Проверяет валидность времени готовки.
        """
        cooking_time = value

        if cooking_time < COOKING_TIME_MIN_VALUE:
            raise ValidationError(
                'Время готовки должно быть хотя бы минуту!'
            )
        return value

    def create_ingredients_amounts(self, ingredients, recipe):
        """
        Создает записи о количестве ингредиентов в рецепте.
        """
        IngredientInRecipe.objects.bulk_create(
            [IngredientInRecipe(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        """
        Создает новый рецепт.
        """
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients_amounts(recipe=recipe, ingredients=ingredients)
        return recipe

    def update(self, instance, validated_data):
        """
        Обновляет существующий рецепт.
        """
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients_amounts(
            recipe=instance, ingredients=ingredients)
        instance.save()
        return instance

    def to_representation(self, instance):
        """
        Преобразует объект рецепта в словарь для сериализации.
        """
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadSerializer(instance, context=context).data


class RecipeShortSerializer(ModelSerializer):
    """
    Сериализатор для краткого представления рецепта.
    """
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
