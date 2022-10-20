"""Recipe view module."""
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT)
from rest_framework.viewsets import ModelViewSet

from recipes.filters import NameSearch, RecipeFilter
from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag)
from recipes.pagination import LimitedPagination
from recipes.permissions import IsOwnerOrReadOnly
from recipes.serializers import (FavoritesSerializer, IngredientSerializer,
                                 RecipeModifySerializer, RecipeSerializer,
                                 ShoppingCartSerializer, TagSerializer)

READ_METHODS = ('GET', 'HEAD', 'OPTIONS')


class RecipeView(ModelViewSet):
    """Recepies View"""
    pagination_class = LimitedPagination
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    search_fields = ['is_favorited', 'is_in_shopping_cart']
    serializer_class = RecipeSerializer
    permission_classes = [IsOwnerOrReadOnly, ]

    def get_serializer_class(self):
        if self.request.method in READ_METHODS:
            return RecipeSerializer
        return RecipeModifySerializer

    def perform_create(self, serializer):
        """Create new recipe."""
        serializer.save(
            author=self.request.user
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer = RecipeSerializer(
            instance=serializer.instance,
            context={'request': self.request}
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        serializer = RecipeSerializer(
            instance=serializer.instance,
            context={'request': self.request}
        )
        return Response(
            serializer.data,
            status=HTTP_200_OK
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
        serializer_class=ShoppingCartSerializer
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            user = request.user
            data = {
                'recipe': pk,
                'user': user.id
            }
            context = {'request': request}
            serializer = ShoppingCartSerializer(
                data=data,
                context=context
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)

        if request.method == 'DELETE':
            user = request.user
            recipe = get_object_or_404(Recipe, pk=pk)
            cart = ShoppingCart.objects.get(
                user=user,
                recipe=recipe
            )
            if cart:
                cart.delete()
            return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        detail=True,
        serializer_class=FavoritesSerializer,
        permission_classes=(IsAuthenticated, )
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            user = request.user
            data = {
                'recipe': pk,
                'user': user.id
            }
            context = {'request': request}
            serializer = FavoritesSerializer(
                data=data,
                context=context
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)

        if request.method == 'DELETE':
            user = request.user
            recipe = get_object_or_404(Recipe, pk=pk)
            cart = FavoriteRecipe.objects.get(
                user=user,
                recipe=recipe
            )
            if cart:
                cart.delete()
            return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=['get', ],
        detail=False
    )
    def download_shopping_cart(self, request, pk=None):
        user = request.user
        recipes_in_cart = user.shopping_cart.filter(user=user)
        ingredients = []
        for cart in recipes_in_cart:
            for ingr in cart.recipe.ingredient_recipe.filter(recipe=cart.recipe):
                ingredients.append(ingr)
        shopping_cart = {}
        for ingredient in ingredients:
            name = ingredient.ingredient.name
            measurement_unit = ingredient.ingredient.measurement_unit
            amount = ingredient.amount
            current_state = shopping_cart.get(
                name, {'amount': 0, 'measurement_unit': measurement_unit}
            )
            current_state['amount'] = current_state.get('amount', 0) + amount
            shopping_cart[name] = current_state
        result = ''
        for ingredient, values in shopping_cart.items():
            result += (
                f'{ingredient}({values["measurement_unit"]})'
                f' - {values["amount"]}\n'
            )
        content = HttpResponse(result, 'Content-Type: text/plain,charset=utf8')
        content['Content-Disposition'] = 'attachment;filename="shopping_list.txt"'
        return content


class TagView(ModelViewSet):
    """Tags View"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngridientView(ModelViewSet):
    """Ingredient View"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [NameSearch, ]
    search_fields = ['^name']
