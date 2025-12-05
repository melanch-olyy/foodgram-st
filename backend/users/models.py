from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from foodgram.constants import MAX_LENGTH_EMAIL, MAX_LENGTH_NAME


class User(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(
        'Email',
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
    username = models.CharField(
        'Никнейм',
        max_length=MAX_LENGTH_NAME,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Никнейм содержит недопустимые символы'
        )]
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/',
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписки на автора."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор'
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
        return f'{self.user} подписан на {self.author}'
