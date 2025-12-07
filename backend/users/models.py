from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from foodgram.constants import MAX_LENGTH_EMAIL, MAX_LENGTH_NAME


class SomeUser(AbstractUser):
    """Модель пользователей платформы Foodgram."""

    username = models.CharField(
        'Уникальный юзернейм',
        max_length=MAX_LENGTH_NAME,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Имя пользователя содержит недопустимые символы.'
        )]
    )
    email = models.EmailField(
        'Адрес электронной почты',
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_LENGTH_NAME
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LENGTH_NAME
    )
    avatar = models.ImageField(
        'Фотография профиля',
        upload_to='users/',
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Система подписок."""

    user = models.ForeignKey(
        SomeUser,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Кто подписался'
    )
    author = models.ForeignKey(
        SomeUser,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='На кого подписались'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]

    def __str__(self):
        return f'{self.user.username} -> {self.author.username}'
