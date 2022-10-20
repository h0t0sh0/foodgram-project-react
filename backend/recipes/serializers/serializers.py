"""Serializers for Recipe app."""

import base64

from django.core.files.base import ContentFile
# from django_filters.rest_framework.filters import ModelMultipleChoiceFilter
from recipes.models import (FavoriteRecipe, Ingredient, IngredientRecipe,
                            Recipe, ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from users.serializers import UserCustomSerializer


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format_name, imgstr = data.split(';base64,')
            ext = format_name.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = [
            'id',
            'name',
            'measurement_unit',
            'amount',
        ]


class IngredientWriteRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ['id', 'amount']


class RecipeModifySerializer(serializers.ModelSerializer):
    ingredients = IngredientWriteRecipeSerializer(many=True)
    tags = serializers.ListField(
        child=serializers.SlugRelatedField(
            queryset=Tag.objects.all(),
            slug_field='id'
        )
    )
    image = Base64ImageField(required=False, allow_null=True)
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Recipe
        fields = [
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author'
        ]

    @staticmethod
    def add_ingredients(recipe, ingredients):
        """Add ingredients for recipe."""
        IngredientRecipe.objects.bulk_create(
            IngredientRecipe(
                ingredient=ingr['id'],
                recipe=recipe,
                amount=ingr['amount']
            ) for ingr in ingredients
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.ingredients.clear()
        ingredients = validated_data.pop('ingredients')
        self.add_ingredients(instance, ingredients)
        return super().update(instance, validated_data)


class RecipeSerializer(serializers.ModelSerializer):
    author = UserCustomSerializer()
    # author = serializers.HiddenField(
    #     default=serializers.CurrentUserDefault()
    # )
    tags = TagSerializer(
        read_only=True,
        many=True,
    )
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]

    def get_ingredients(self, obj):
        """Check ingredients method."""
        ingr = IngredientRecipe.objects.filter(
            recipe=obj.id
        )
        serializer = IngredientRecipeSerializer(ingr, many=True)

        return serializer.data

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return FavoriteRecipe.objects.filter(
            user=user,
            recipe=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return ShoppingCart.objects.filter(
            user=user,
            recipe=obj.id
        ).exists()


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ['user', 'recipe']
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Already in shopping cart'
            )
        ]

    def to_representation(self, instance):
        context = {'request': self.context['request']}
        return RecipeSerializer(
            instance.recipe,
            context=context
        ).data


class FavoritesSerializer(serializers.ModelSerializer):

    class Meta:
        model = FavoriteRecipe
        fields = ['user', 'recipe']
        validators = [
            UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=('user', 'recipe'),
                message='Already in favorites'
            )
        ]

    def to_representation(self, instance):
        context = {'request': self.context['request']}
        return RecipeSerializer(
            instance.recipe,
            context=context
        ).data
