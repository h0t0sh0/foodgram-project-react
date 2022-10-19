# Generated by Django 4.1 on 2022-09-19 17:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ComponentRecipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "amount",
                    models.PositiveIntegerField(verbose_name="Component amount"),
                ),
                (
                    "component",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="component_recipe",
                        to="recipes.component",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="component_recipe",
                        to="recipes.recipe",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="componentrecipe",
            constraint=models.UniqueConstraint(
                fields=("component", "recipe"), name="component_amount_constraint"
            ),
        ),
    ]