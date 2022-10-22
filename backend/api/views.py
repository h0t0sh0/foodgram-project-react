"""Api view module."""
from api.permissions import IsOwnerOrReadOnly
from api.serializers import (FavoritesSerializer, IngredientSerializer,
                             RecipeModifySerializer, RecipeSerializer,
                             ShoppingCartSerializer,
                             SubscriptionListSerializer,
                             SubscriptionSerializer, TagSerializer)
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.filters import NameSearch, RecipeFilter
from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag)
from recipes.pagination import LimitedPagination
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND)
from rest_framework.viewsets import ModelViewSet
from users.models import SubscribeUser, User


class RecipeView(ModelViewSet):
    """Recepies View"""
    pagination_class = LimitedPagination
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    search_fields = ['is_favorited', 'is_in_shopping_cart']
    serializer_class = RecipeSerializer
    permission_classes = [IsOwnerOrReadOnly, ]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
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

    def user_action(self, request, model, serializer, pk):
        if request.method == 'POST':
            user = request.user
            data = {
                'recipe': pk,
                'user': user.id
            }
            context = {'request': request}
            serializer_action = serializer(
                data=data,
                context=context
            )
            serializer_action.is_valid(raise_exception=True)
            serializer_action.save()
            return Response(serializer_action.data, status=HTTP_201_CREATED)

        if request.method == 'DELETE':
            user = request.user
            recipe = get_object_or_404(Recipe, pk=pk)
            cart = model.objects.get(
                user=user,
                recipe=recipe
            )
            if cart:
                cart.delete()
            return Response(status=HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        detail=True,
        serializer_class=ShoppingCartSerializer
    )
    def shopping_cart(self, request, pk=None):
        return self.user_action(
            request,
            ShoppingCart,
            ShoppingCartSerializer,
            pk
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
        serializer_class=FavoritesSerializer,
        permission_classes=(IsAuthenticated, )
    )
    def favorite(self, request, pk=None):
        return self.user_action(
            request,
            FavoriteRecipe,
            FavoritesSerializer,
            pk
        )

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


class UserView(UserViewSet):
    pagination_class = LimitedPagination

    @action(
        methods=['post', 'delete'],
        detail=True,
        serializer_class=SubscriptionSerializer
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, pk=id)
        if request.method == 'POST':
            data = {
                'user': user.id,
                'author': author.id
            }
            context = {'request': request}

            serializer = SubscriptionSerializer(
                data=data,
                context=context
            )

            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=HTTP_201_CREATED)
        if request.method == 'DELETE':
            try:
                SubscribeUser.objects.get(user=user, author=author).delete()
            except SubscribeUser.DoesNotExist:
                data = {'detail': 'Page not found.'}
                return Response(data, status=HTTP_404_NOT_FOUND)
            return Response(status=HTTP_204_NO_CONTENT)

    def get_subscribtion_serializer(self, *args, **kwargs):
        kwargs.setdefault('context', self.get_serializer_context())
        kwargs['context']['recipes_limit'] = self.request.query_params.get('recipes_limit')
        return SubscriptionListSerializer(*args, **kwargs)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=[IsAuthenticated, ]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(
            subscriber_author__user=user
        )
        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_subscribtion_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_subscribtion_serializer(queryset, many=True)
        return Response(serializer.data, status=HTTP_200_OK)
