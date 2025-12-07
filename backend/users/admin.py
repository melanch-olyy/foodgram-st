from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import SomeUser, Subscription


@admin.register(SomeUser)
class UserAdminConfig(UserAdmin):
    """Настройка админки для кастомной модели пользователя."""

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'id',
    )
    list_filter = ('email', 'username')
    search_fields = ('username', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('avatar',)}),
    )
    empty_value_display = '-пусто-'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админка для подписок."""

    list_display = ('user', 'author')
    search_fields = (
        'user__username',
        'user__email',
        'author__username',
        'author__email'
    )
    empty_value_display = '-пусто-'
