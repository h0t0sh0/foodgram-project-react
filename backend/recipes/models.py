from django.db import models
from users.models import User

DEFAULT_COLOR = '#ffffff'


class AbstractModel(models.Model):
    """Abstract Model"""
    name = models.TextField(
        'Name',
        max_length=200
    )

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.name)


class Ingredient(AbstractModel):
    """Component class"""
    measurement_unit = models.TextField(
        'Measurement unit',
        max_length=200
    )


class Tag(AbstractModel):
    """Tag class"""
    color = models.TextField(
        'HexColor',
        max_length=7,
        default=DEFAULT_COLOR
    )

    slug = models.TextField(
        'Slug',
        max_length=256,
        blank=True,
        null=True
    )


class Recipe(AbstractModel):
    """Recepie class"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )

    image = models.ImageField(
        upload_to='recipe_images/',
        editable=True
    )

    text = models.TextField('Description')

    tags = models.ManyToManyField(Tag)

    cooking_time = models.PositiveIntegerField(
        'Cooking time in minutes'
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe'
    )

    class Meta:
        ordering = ('-id', )

    def _favorites_count(self):
        return self.favorites.count()

    def __str__(self):
        return f'Recipe: {self.name}'


class IngredientRecipe(models.Model):
    """Ingredients amount for recipe."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe'
    )

    amount = models.PositiveIntegerField(
        'Ingredient amount'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='ingredient_amount_constraint'
            )
        ]


class FavoriteRecipe(models.Model):
    """Favorite recipes for user."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='favorite_recipes_constraint'
            )
        ]


class ShoppingCart(models.Model):
    """Shopping Cart for user."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='user_shopping_cart_constraint'
            )
        ]
