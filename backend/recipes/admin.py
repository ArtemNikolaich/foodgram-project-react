from django.contrib import admin

from recipes.models import (
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Tag,
    Favorite,
    ShoppingCart
)


class IngredientRecipeInLine(admin.TabularInline):
    model = IngredientInRecipe
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientRecipeInLine,)
    list_display = ('id',
                    'name',
                    'author',
                    'favorite_count',
                    'ingredients_list')
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name',)

    def favorite_count(self, obj):
        return obj.favorites.count()

    favorite_count.short_description = 'Избрано'

    def ingredients_list(self, obj):
        return ", ".join(
            [ingredient.name for ingredient
             in obj.ingredients.all()]
        )

    ingredients_list.short_description = 'Ингредиенты'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('measurement_unit',)
    search_fields = ('name',)


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
