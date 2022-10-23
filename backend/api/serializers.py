"""Serializers for api."""

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField

from recipes.models import FavoriteRecipe, Ingredient, IngredientRecipe, Recipe, ShoppingCart, Tag
from users.models import SubscribeUser, User

POSITIVE_ERROR = 'Expecting {} as positive number'
EMPTY_ERROR = 'Minimun one {} required'


class UserCustomSerializer(UserSerializer):

    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.id:
            return SubscribeUser.objects.filter(
                user=user,
                author=obj.id
            ).exists()
        return False


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

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError(POSITIVE_ERROR.format('amount'))


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

    def validate_cooking_time(self, value):
        if int(value) < 1:
            raise serializers.ValidationError(POSITIVE_ERROR.format('cooking_time'))
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(EMPTY_ERROR.format('ingredient'))
        for item in value:
            if item['amount'] < 0:
                raise serializers.ValidationError(POSITIVE_ERROR.format('itgredient_amount'))
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError(EMPTY_ERROR.format('tag'))
        return value

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
        instance.tags.set(validated_data['tags'])
        instance.ingredients.clear()
        ingredients = validated_data.pop('ingredients')
        self.add_ingredients(instance, ingredients)
        return super().update(instance, validated_data)


class RecipeSerializer(serializers.ModelSerializer):
    author = UserCustomSerializer()
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
        if user.is_authenticated:
            return FavoriteRecipe.objects.filter(
                user=user,
                recipe=obj.id
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=user,
                recipe=obj.id
            ).exists()
        return False


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


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubscribeUser
        fields = ['user', 'author']
        validators = [
            UniqueTogetherValidator(
                queryset=SubscribeUser.objects.all(),
                fields=('user', 'author'),
                message='Already subscribed'
            )
        ]


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time'
        ]


class SubscriptionListSerializer(serializers.ModelSerializer):

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = [*UserSerializer.Meta.fields, 'recipes', 'recipes_count']

    def get_recipes(self, obj):
        recipes_limit = self.context.get('recipes_limit', False)
        if recipes_limit:
            recipes_limit = int(recipes_limit)
            recipes = Recipe.objects.filter(author=obj)[:recipes_limit]
        else:
            recipes = Recipe.objects.filter(author=obj)
        serializer = RecipeShortSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
