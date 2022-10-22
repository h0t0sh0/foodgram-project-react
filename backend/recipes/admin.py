from django.contrib import admin
from recipes.models import (Ingredient, IngredientRecipe, Recipe, ShoppingCart,
                            Tag)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', )
    list_filter = ('name', )
    empty_value_display = '-empty-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')
    empty_value_display = '-empty-'


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'text',
        'cooking_time',
        '_favorites_count'
    )
    search_fields = (
        'name',
        'author',
        'text',
        'tags'
    )
    list_filter = (
        'name',
        'author',
        'tags'
    )
    empty_value_display = '-empty-'


class IngredientRecipeAdmin(admin.ModelAdmin):
    list_display = (
        'ingredient',
        'recipe',
        'amount'
    )
    search_fields = (
        'ingredient',
        'recipe'
    )
    list_filter = (
        'ingredient',
        'recipe'
    )
    empty_value_display = '-empty-'


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientRecipe, IngredientRecipeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
