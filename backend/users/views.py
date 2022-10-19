from django.shortcuts import get_object_or_404

from djoser.views import UserViewSet
from recipes.pagination import LimitedPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND)
from users.models import SubscribeUser, User
from users.serializers import (SubscriptionListSerializer,
                               SubscriptionSerializer)


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
