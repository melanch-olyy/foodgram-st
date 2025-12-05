from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'pub_date')
    search_fields = ('name', 'author__username')
    list_filter = ('author', 'name', 'pub_date')
    inlines = (RecipeIngredientInline,)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    empty_value_display = '-пусто-'


admin.site.register(Favorite)
admin.site.register(ShoppingCart)
