from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe, Tag
from rest_framework.filters import SearchFilter


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        lookup_expr='iexact',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = [
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart'
        ]

    def get_is_favorited(self, queryset, name, value):
        if value:
            favor_recipes = (
                self.request.user.favorites.filter(
                    user=self.request.user
                )
            )
        return queryset.filter(
            pk__in=(favor.recipe.pk for favor in favor_recipes)
        )

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            cart_recipes = (
                self.request.user.shopping_cart.filter(
                    user=self.request.user
                )
            )
            return queryset.filter(
                pk__in=(cart.recipe.pk for cart in cart_recipes)
            )
        return queryset


class NameSearch(SearchFilter):
    search_param = 'name'
