from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    email = models.EmailField(
        verbose_name='Email',
        max_length=254,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='First Name',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Last Name',
        max_length=150,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['-pk', ]


class SubscribeUser(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber_author'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='subscription_constraint'
            )
        ]
