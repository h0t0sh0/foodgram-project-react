from djoser.serializers import UserSerializer
from recipes.models import Recipe
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import SubscribeUser, User


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
