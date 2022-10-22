from django.urls import include, path

from rest_framework.routers import DefaultRouter

from api.views import IngridientView, RecipeView, TagView, UserView

app_name = 'api'

router = DefaultRouter()

router.register('users', UserView, basename='users')
router.register('tags', TagView, basename='tags')
router.register('recipes', RecipeView, basename='recipes')
router.register('ingredients', IngridientView, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
