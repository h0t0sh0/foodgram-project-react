"""Api view module."""
from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND
)
from rest_framework.viewsets import ModelViewSet

from djoser.views import UserViewSet

from api.permissions import IsOwnerOrReadOnly
from api.serializers import (
    FavoritesSerializer,
    IngredientSerializer,
    RecipeModifySerializer,
    RecipeSerializer,
    ShoppingCartSerializer,
    SubscriptionListSerializer,
    SubscriptionSerializer,
    TagSerializer
)
from recipes.filters import NameSearch, RecipeFilter
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag
)
from recipes.pagination import LimitedPagination
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

        ingredients = IngredientRecipe.objects.filter(
            recipe__in_shopping_cart__user=user
        ).order_by(
            'ingredient__name'
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(sum_amount=Sum('amount'))

        shopping_cart = '\n'.join([
            f'{ingredient["ingredient__name"]}({ingredient["ingredient__measurement_unit"]})'
            f' - {ingredient["sum_amount"]} '
            for ingredient in ingredients
        ])

        content = HttpResponse(shopping_cart, 'Content-Type: text/plain,charset=utf8')
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
    search_fields = ['^name', ]


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
