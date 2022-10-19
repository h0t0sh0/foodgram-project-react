from django.urls import include, path

from recipes.views import IngridientView, RecipeView, TagView
from rest_framework.routers import DefaultRouter
from users.views import UserView

app_name = 'api'

router = DefaultRouter()

router.register(r'users', UserView, basename='users')
router.register(r'tags', TagView, basename='tags')
router.register(r'recipes', RecipeView, basename='recipes')
router.register(r'ingredients', IngridientView, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
