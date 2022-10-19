# Generated by Django 4.1 on 2022-09-28 20:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0005_rename_description_recipe_text"),
    ]

    operations = [
        migrations.AddField(
            model_name="recipe",
            name="ingredients",
            field=models.ManyToManyField(
                through="recipes.IngredientRecipe", to="recipes.ingredient"
            ),
        ),
        migrations.AlterField(
            model_name="ingredient",
            name="measurement_unit",
            field=models.TextField(max_length=200, verbose_name="Measurement unit"),
        ),
        migrations.AlterField(
            model_name="ingredient",
            name="name",
            field=models.TextField(max_length=200, verbose_name="Name"),
        ),
        migrations.AlterField(
            model_name="ingredientrecipe",
            name="ingredient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ingredient_recipe",
                to="recipes.ingredient",
            ),
        ),
        migrations.AlterField(
            model_name="ingredientrecipe",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ingredient_recipe",
                to="recipes.recipe",
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="name",
            field=models.TextField(max_length=200, verbose_name="Name"),
        ),
        migrations.AlterField(
            model_name="tag",
            name="name",
            field=models.TextField(max_length=200, verbose_name="Name"),
        ),
    ]