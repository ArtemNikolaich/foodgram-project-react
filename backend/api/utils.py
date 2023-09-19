from datetime import datetime
from django.http import HttpResponse
from django.db.models import Sum

from foodgram.constants import CONTENT_TYPE, FILENAME
from recipes.models import IngredientInRecipe


def generate_shopping_cart_content(user):
    """
    Генерирует содержимое списка покупок для корзины пользователя.
    """
    ingredients = IngredientInRecipe.objects.filter(
        recipe__shopping_cart__user=user).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
                amount=Sum('amount')
    )
    return ingredients


def create_shopping_cart_response(user):
    """
    Создает HTTP-ответ с содержимым списка покупок для корзины пользователя.
    """
    ingredients = generate_shopping_cart_content(user)
    today = datetime.today()
    content = (
        f'Foodgram. {today:%Y.%m.%d, %H:%M}\n'
        f'Список покупок для: {user.get_full_name()}\n\n'
    )
    content += '\n'.join([
        f'- {ingredient["ingredient__name"]}, '
        f'{ingredient["ingredient__measurement_unit"]}: '
        f'{ingredient["amount"]}'
        for ingredient in ingredients
    ])

    response = HttpResponse(content, content_type=CONTENT_TYPE)
    response['Content-Disposition'] = f'attachment; filename={FILENAME}'
    return response
