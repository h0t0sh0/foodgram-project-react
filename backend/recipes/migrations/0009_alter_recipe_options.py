# Generated by Django 4.1 on 2022-10-20 10:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("recipes", "0008_remove_favoriterecipe_favorite_recipes_constraint_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="recipe",
            options={"ordering": ("-id",)},
        ),
    ]
